# **Merkle Tree Game**

Welcome to the **Merkle Tree Game**, an  **blockchain-based Algorand game**, developed using the **[PyTeal](https://github.com/algorand/pyteal)** and **[Beaker](https://github.com/algorand-devrel/beaker)** frameworks. 🚀

## **Game Specifications**
The **Merkle Tree Game** involves two main roles: the game creator and the participants. The game creator publishes the root of a Merkle Tree along with its height, challenging participants to discover all the leaves of the tree.

The creator is constrained to generate leaves using a randomness factor $r$, published alongside the Merkle Tree root. The leaf generation follows the formula:
$$leaf_i = (num||r)_{num\in[0,100)}$$

The winner is the participant who successfully finds all Merkle Tree leaves and verifies the correctness of the Merkle Tree given a $path$ and a $leaf$. The winner receives an Algo prize, which can be publicly verified even before participating in the game.

The Merkle Tree implementation serves the dual purpose of storing only the root within the smart contract, ensuring efficient verification with logarithmic complexity relative to the number of leaves.

## **Project Overview**
This project was chosen not only for learning the **PyTeal** language and its syntax but also for exploring how to interface (using sha256) and implement (using a Merkle Tree) **cryptographic primitives** within an Algorand smart contract. Additionally, it delves into **managing payments and transactions** within an Algorand smart contract.

### **Observations and Future Developments**

It's crucial to note that, in this context, the game creator has no actual constraints on leaf creation. There is a potential for the creator to generate leaves that do not adhere to the specified form $leaf_i = (num||r)_{num\in[0,100)}$. An interesting future development could involve implementing a zero-knowledge verification mechanism. This would allow publicly verifying that the leaves were created correctly without revealing their actual values. 🌱🔐