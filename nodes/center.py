from nodes.base import Base
from framework import factory
from common import config, logging, KeyManager
from utils import value_dispatch, Msg

@factory("nodes.Center")
class Center(Base):
    _instance = None

    def __new__(cls, addr=None, config=..., *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        else:
            logging.error("class Center is singleton, should be instanced only once.")
            exit(-1)
        return cls._instance

    def __init__(self, addr=None, config=...) -> None:
        super().__init__(addr, config)
        self.client2key = dict()

    @value_dispatch
    def handle_msg(self, type, msg, addr):
        logging.error(f"unexpected msg type:{type} with msg:{msg}, please check.")
        return False

    @handle_msg.register(Msg.INIT_SESSION_REQUEST)
    def _(self, type, msg, addr):
        pub_key = msg.get("client-pub", None)
        client_addr = msg.get("client-addr", None)
        if pub_key is None:
            logging.error(f"{type} have not client-pub section. Handle msg failed.")
            return False
        if client_addr is None:
            logging.error(f"{type} have not client-addr section. Handle msg failed.")
        key = KeyManager.generate_key()
        encrypt_key = KeyManager.encrypt_with_pub(key, pub_key)
        self.client2key[tuple(client_addr)] = key
        logging.info(f"super {self.addr} generate key {key}")
        self.rpc.send(
            {
                "type": Msg.INIT_SEESION_RESPONSE,
                "encrypt-key": encrypt_key.hex(),  # to string, 以使其能被json化
                "client-addr": client_addr,
            },
            addr,
        )