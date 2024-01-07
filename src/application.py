from pyteal import *
import beaker
from typing import Literal as L

LEFT_PREFIX = Int(0)

class MerkleTreeState:
    root = beaker.GlobalStateValue(stack_type=TealType.bytes,static=True)
    size = beaker.GlobalStateValue(stack_type=TealType.uint64,static=True)
    balance = beaker.GlobalStateValue(stack_type=TealType.uint64)
    r = beaker.GlobalStateValue(stack_type=TealType.bytes,static=True)

app = beaker.Application("MerkleTree",state = MerkleTreeState())


@app.create
def on_create(height: abi.Uint64, root: abi.DynamicBytes, r: abi.DynamicBytes) -> Expr:
    """
    Creates the Merkle Tree  game application.
    :param height: The height of the Merkle Tree.
    :param root: The root of the Merkle Tree.
    :param r: The randomness to use in the leaves.
    """
    return  Seq([app.state.size.set(height.get()),
                 app.state.root.set(root.get()),
                 app.state.balance.set(Int(0)),
                 app.state.r.set(r.get())])
    
@app.external
def start_game(payment: abi.PaymentTransaction) -> Expr:
    """
    Starts the Merkle Tree game. Adding Algos to the contract.
    :param payment: The payment transaction that adds Algos to the contract.
    """
    return Seq([Assert(payment.get().receiver() == Global.current_application_address()),
                Assert(payment.get().amount() > Int(0)),
                app.state.balance.set(payment.get().amount()),
            ])

@app.external(read_only=True)    
def get_size(*,output: abi.Uint64) -> Expr:
    """
    Returns the size of the Merkle Tree.
    """
    return output.set(app.state.size)

@app.external(read_only=True)    
def get_root(*,output: abi.DynamicBytes) -> Expr:
    """
    Returns the root of the Merkle Tree.
    """
    return output.set(app.state.root)

@app.external(read_only=True)
def verify_leaf(data: abi.String, path: abi.DynamicArray[abi.StaticBytes[L[33]]]) -> Expr:
    """
    Verifies that the leaf is in the Merkle Tree.
    :param data: The leaf to verify.
    :param path: The path to the leaf. That is composed of the nodes from the leaf to the root, of 33 bytes each. The first byte is the prefix (0 for left, 1 for right).
    """
    return Seq([Assert(app.state.size == path.length()),
                Assert(app.state.balance > Int(0)),
                Assert(app.state.root == calculate_root(Sha256(Concat(data.get(),app.state.r)), path)),
                pay_winner(),
                app.state.balance.set(Int(0)),
            ])



@Subroutine(TealType.bytes)
def calculate_root(leaf: Expr, path: abi.DynamicArray[abi.StaticBytes[L[33]]]) -> Expr:
    """
    Calculates the root of the Merkle Tree, starting from a leaf and a the path.
    :param leaf: The leaf to start from.
    :param path: The path to the leaf. That is composed of the nodes from the leaf to the root, of 33 bytes each. The first byte is the prefix (0 for left, 1 for right).
    """
    result = ScratchVar(TealType.bytes)
    i = ScratchVar(TealType.uint64)

    path_node = abi.make(abi.StaticBytes[L[33]])
    return Seq ([result.store(leaf),
                 For(i.store(Int(0)), i.load() < path.length(), i.store(i.load() + Int(1))).Do(
                        path_node.set(path[i.load()]),
                        result.store(
                            If(GetByte(path_node.get(),Int(0)) == LEFT_PREFIX).Then(
                                Sha256(Concat(result.load(), Extract(path_node.get(), Int(1), Int(32))))
                            ).Else(
                                Sha256(Concat(Extract(path_node.get(), Int(1), Int(32)), result.load()))
                            )
                        )
                    ),
                 Return(result.load())
            ])

@Subroutine(TealType.none)
def pay_winner()->Expr:
    """
    Pays the winner of the game.
    """
    return Seq([InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields({
                    TxnField.type_enum: TxnType.Payment,
                    TxnField.amount: app.state.balance - Int(1000),
                    TxnField.receiver: Txn.sender(),
                    
                }),
                InnerTxnBuilder.Submit()
            ])

@app.external(read_only=True)
def get_balance(*,output: abi.Uint64)->Expr:
    """
    Returns the balance of the contract.
    """
    return output.set(Balance(Global.current_application_address()))

@app.external(read_only=True)
def account_balance(*,output: abi.Uint64)->Expr:
    """
    Returns the balance of the account that called the method.
    """
    return output.set(Balance(Txn.sender()))