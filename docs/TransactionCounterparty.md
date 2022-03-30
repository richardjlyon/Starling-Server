```mermaid
 
 erDiagram
    Transaction ||--o{ Counterparty : has
    Transaction ||--o{ Category : has
    Category ||--o{ CategoryGroup : has
    
    Counterparty {
        string name
        string display_name
    }
    
    NameDisplayname {
        string name
        string name_fragment
        string display_name
    }
 
```