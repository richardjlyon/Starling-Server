module default {
    type Bank {
        required property name -> str {constraint exclusive;};
        multi link accounts -> Account;
    }

    type Account {
        required property uuid -> uuid {constraint exclusive;};
        required property name -> str;
        required property currency -> str;
        property created_at -> datetime;
        multi link transactions -> Transaction
    }

    type Transaction {
        required property uuid -> uuid {constraint exclusive;};
        required property time -> datetime;
        required property counterparty_name -> str;
        required property amount -> float32;
        link category -> Category;
        property reference -> str;
    }

    type Category {
        required property name -> str;
        multi link transactions -> Transaction;
    }

    type CategoryGroup {
        required property name -> str;
        multi link categories -> Category;
    }
}
