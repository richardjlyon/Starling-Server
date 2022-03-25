```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant RouteManager
    participant ProviderAPI
    participant TransactionManager
    participant Database
    Client->>FastAPI: /transaction
    activate FastAPI
    FastAPI->> RouteManager: /transaction
    activate RouteManager
    RouteManager ->> ProviderAPI: /transaction
    activate ProviderAPI
    ProviderAPI ->> RouteManager: [TransactionSchema]
    deactivate ProviderAPI
    RouteManager ->> Database: upsert [TransactionSchema]
    activate Database
    RouteManager ->> TransactionManager: assign category / display name
    activate TransactionManager
    TransactionManager ->> Database: upsert category / display names
    deactivate TransactionManager
    Database ->> RouteManager: select transactions
    deactivate Database
    RouteManager ->> FastAPI: return transactions
    deactivate RouteManager
    FastAPI ->> Client: return transactions
    deactivate FastAPI