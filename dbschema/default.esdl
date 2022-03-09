module default {
    type Account {
        required property uuid -> uuid {constraint exclusive;};
        required property bank_name -> str {constraint exclusive;};
        required property account_name -> str;
        required property currency -> str;
        property created_at -> datetime;
        multi link transactions -> Transaction {constraint exclusive};
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
