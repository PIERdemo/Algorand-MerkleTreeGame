from beaker import client, localnet, consts
from application import app
from algosdk.atomic_transaction_composer import TransactionWithSigner
from algosdk import transaction

to_hex = lambda x: ''.join(format(b, '02x') for b in x)
construct_path = lambda path: [(b'\x01' if node[0] else b'\x00') + bytes.fromhex(node[1]) for node in path] # 1 if is right
address = lambda x: f"{x.address[:3]}...{x.address[-3:]}"

def build_app(sender):
    app.build().export("./artifacts")

    app_client = client.ApplicationClient(
        client=localnet.get_algod_client(),
        app = app,
        sender = sender.address,
        signer=sender.signer
    )
    return app_client

def concat_hashsha256(data1, data2):
    import hashlib
    return hashlib.sha256(data1 + data2).digest()


if __name__ == "__main__":
    HEIGHT = 2
    LEAF = "8"
    RANDOMNESS = b"DataPrivacyAndSecurity"
    ROOT = bytes.fromhex("7da0897bb98675d12e32de867c17ec51ff7be34e7e6e8ef543ed8137e251a913")
    
    PATH = construct_path([(True,"5a6dc64be895a087669e6d287eaeaa4a089604700703e70d01310b6e559dd117"),
                           (True,"7077f8ccecfa205fe9097a846af39c166f6f13a6953234e60eac82c9b7e92e6c")])
    AMOUNT = 1*consts.algo   

    owner = localnet.kmd.get_accounts()[0]
    player = localnet.kmd.get_accounts()[1]

    app_client = build_app(owner)
    app_id,app_addr,txid = app_client.create(height=HEIGHT, root=ROOT, r=RANDOMNESS)
    print(f"[USER: {address(owner)}] Created app with id:", app_id)
    print(f"[USER: {address(owner)}] Set up the game with root:", to_hex(ROOT)[:5],"...")

    return_tx = app_client.call("account_balance")
    print(f"[USER: {address(owner)}] Check his own balance: {return_tx.return_value}")
    
    payment = TransactionWithSigner(signer=owner.signer,
                                    txn=transaction.PaymentTxn(sender= owner.address,
                                                               sp=localnet.get_algod_client().suggested_params(),
                                                               receiver=app_addr,
                                                               amt=AMOUNT))
    return_tx = app_client.call("start_game", payment=payment)
    print(f"[USER: {address(owner)}] Started game with reward:", AMOUNT, "Algos")

    return_tx = app_client.call("account_balance")
    print(f"[USER: {address(owner)}] Check his own balance: {return_tx.return_value}")

    print("\n","=-="*20,"\n")
    app_client_player = app_client.prepare(signer = player.signer)
    return_tx = app_client_player.call("get_balance")
    print(f"[USER: {address(player)}] Check the balance: {return_tx.return_value}")

    return_tx = app_client_player.call("account_balance")
    print(f"[USER: {address(owner)}] Check his own balance: {return_tx.return_value}")

    try:
        return_tx = app_client_player.call("verify_leaf", data = LEAF, path = PATH)
        print(f"[USER: {address(player)}] Win with \n\tleaf {LEAF} \n\twith path {[to_hex(node) for node in PATH]}")
    except Exception:
        print(f"[USER: {address(player)}] Lose with \n\tleaf {LEAF} \n\twith path {[to_hex(node) for node in PATH]}")
    
    return_tx = app_client_player.call("account_balance")
    print(f"[USER: {address(owner)}] Check his own balance: {return_tx.return_value}")