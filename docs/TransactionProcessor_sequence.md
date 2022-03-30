```mermaid
sequenceDiagram
    participant RouteDispatcher
    participant TransactionProcessor
    participant Database
    
    RouteDispatcher -> TransactionProcessor: "Send transaction to TransactionProcessor"
    activate TransactionProcessor
    
```