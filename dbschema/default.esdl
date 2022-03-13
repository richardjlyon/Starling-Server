module default {
    type Bank {
        required property name -> str {constraint exclusive};
        multi link accounts := .<bank[is Account];
    }

    type Account {
        required link bank -> Bank;
        required property uuid -> uuid {constraint exclusive};
        required property name -> str;
        required property currency -> str;
        property created_at -> datetime;
        property server_last_updated -> datetime;
        multi link transactions := .<account[is Transaction];
    }

    type Transaction {
        required link account -> Account;
        required property uuid -> uuid {constraint exclusive};
        required property time -> datetime;
        required property counterparty_name -> str;
        required property amount -> float32;
        property reference -> str;
        link category -> Category;
    }

    type CategoryGroup {
        required property name -> str;
        multi link categories -> Category { constraint exclusive };
    }

    type Category {
        required property name -> str;
        multi link transactions := .<category[is Transaction];
    }
}