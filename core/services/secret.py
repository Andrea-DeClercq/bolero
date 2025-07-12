#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib
from base64 import b64encode, b64decode, b32encode, b32decode
from binascii import hexlify, unhexlify

# Imports from external libraries
from Crypto import Random
from Crypto.Cipher import AES, Blowfish
from Crypto.Util.Padding import pad, unpad

# Import from local code
from config import settings
from core.services.tools_belt import humps
import core.services.jsonlib as json

codecs = dict()


class _BaseCodec:
    _CipherCls = None
    _CipherModeCls = None

    def __init_subclass__(cls, **kwargs):
        """
        Enregistre dans _codecs toutes les classes héritants de _BaseCodec
        """
        super().__init_subclass__(**kwargs)
        key = cls.__name__.replace("_Codec_", "")
        key = humps.snakize(key)
        codecs[key] = cls

    def __init__(self, key, iv=None):
        self.key = key
        self.iv = self.get_iv() if not iv else iv
        self.cipher = self.generate_cipher()

    @property
    def _block_size(self):
        return self._CipherCls.block_size

    def encrypt(self, *args, **kwargs):
        return self.cipher.encrypt(*args, **kwargs)

    def decrypt(self, *args, **kwargs):
        return self.cipher.decrypt(*args, **kwargs)

    def generate_cipher(self):
        kwargs = {
            "key": self.key,
            "mode": self._CipherModeCls,
        }
        if self.iv:
            kwargs["iv"] = self.iv
        return self._CipherCls.new(**kwargs)

    def get_iv(self):
        return Random.get_random_bytes(self._CipherCls.block_size)

    def pre_encrypt(self, data):
        return pad(data, self._block_size)

    def post_decrypt(self, data):
        return unpad(data, self._block_size)


class _Codec_AES_128_CBC(_BaseCodec):
    _CipherCls = AES
    _CipherModeCls = AES.MODE_CBC


class _Codec_AES_128_ECB(_BaseCodec):
    _CipherCls = AES
    _CipherModeCls = AES.MODE_ECB

    def get_iv(self):
        return None


class _Codec_BLOWFISH_ECB(_BaseCodec):
    _CipherCls = Blowfish
    _CipherModeCls = Blowfish.MODE_ECB

    def get_iv(self):
        return None


class _DIRTY_CAIRN_COUNTER_ALGO:
    """
    En raison d'une erreur d'interprétation, les octets de bourrage sur la chaine chiffrée
    qui sont attendus sur le counter-v5 de cairn sont uniquement du \x00 au lieu d'être que du
    \x06 ou une suite \x06\x00\x00…
    Donc, pour éviter de devoir renvoyer les clés aux éditeurs, on préfère créer un chiffrement
    un peu custom
    """

    def pre_encrypt(self, data):
        data = super().pre_encrypt(data)
        # Remplacement des octets \x06 utilisé par blowfish par défaut en \x00
        # Une boucle inversée est utilisée parce qu'un replace ou une regexp risquait de filter
        # les octets vides au milieu des données sans qu'ils ne soient des octets de bourrage
        data = list(data)[::-1]
        for index, char in enumerate(data):
            if char == 6:
                data[index] = 0
                continue
            break
        return bytes(data[::-1])

    def post_decrypt(self, data):
        data = list(data)[::-1]
        for index, char in enumerate(data):
            if char == 0:
                data[index] = 6
                continue
            break
        return super().post_decrypt(bytes(data[::-1]))


class _Codec_DIRTY_CAIRN_COUNTER_BLOWFISH_ECB(_DIRTY_CAIRN_COUNTER_ALGO, _Codec_BLOWFISH_ECB):
    pass


class Secret:
    def __init__(self, algo, key, decode_key=True, **kwargs):
        self.algo = humps.snakize(algo)
        if isinstance(key, str):
            if decode_key:
                self.key = b64decode(key)
            else:
                self.key = key.encode("utf-8")
        else:
            self.key = key
        try:
            self.codec = codecs[self.algo](self.key, **kwargs)
        except KeyError:
            raise KeyError(
                "Secret algo must be in [{}], get {}".format(
                    "|".join(codecs.keys()),
                    self.algo,
                )
            )

    def _get_base_encoder(self, base=64):
        if isinstance(base, int):
            base = str(base)
        if base == "32":
            return b32encode
        if base == "64":
            return b64encode
        if base == "hex":
            return hexlify
        raise NotImplementedError()

    def _get_base_decoder(self, base=64):
        if isinstance(base, int):
            base = str(base)
        if base == "32":
            return b32decode
        if base == "64":
            return b64decode
        if base == "hex":
            return unhexlify
        raise NotImplementedError()

    def encrypt(self, data, json_encode=True, url_encode=True, base_encode=64, with_iv=True):
        if json_encode:
            data = json.dumps(data)
        data = self.codec.pre_encrypt(data.encode("utf-8"))
        encrypt_data = self.codec.encrypt(data)
        # Encodage en vue d'un passage dans une url par exemple
        # L'underscore est choisi car il n'est pas dans l'alphabet base64
        encrypt_data = [encrypt_data]
        if with_iv:
            encrypt_data.insert(0, self.codec.iv)
        base_encoder = self._get_base_encoder(base_encode)
        encrypt_data = [base_encoder(p).decode("ascii") for p in encrypt_data if p]
        encrypt_data = "_".join(encrypt_data)
        if url_encode:
            encrypt_data = humps.urlize(encrypt_data)
        return encrypt_data

    def decrypt(self, encrypt_data, json_decode=True, base_decode=64):
        # Décodage depuis une url, si besoin
        encrypt_data = humps.unurlize(encrypt_data)
        base_decoder = self._get_base_decoder(base_decode)
        if "_" in encrypt_data:
            # Avec une IV
            iv, encrypt_data = [base_decoder(p) for p in encrypt_data.split("_")]
            # Ici, obligé de reinstancier un nouvel cipher parce que nous ne connaissons l'IV qu'à la récéption
            codec = codecs[self.algo](self.key, iv)
        else:
            # Sans IV
            encrypt_data = base_decoder(encrypt_data)
            codec = self.codec
        data = codec.decrypt(encrypt_data)
        data = codec.post_decrypt(data)
        if json_decode:
            data = json.loads(data)
        else:
            data = data.decode("utf-8")
        return data


class RealmSecret(Secret):
    def __init__(self, algo, realm, *args, **kwargs):
        base_config = settings.auth.cross_site
        config = dict(base_config.common, **base_config.realms[realm])
        super().__init__(algo, config["key"], *args, **kwargs)
