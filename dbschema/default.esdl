module default {
    type Bank {
        required property name -> str {constraint exclusive};
        required property auth_token_hash -> str;
        multi link accounts := .<bank[is Account];
    }

    type Account {
        required link bank -> Bank {
            on target delete delete source;
        };
        multi link transactions := .<account[is Transaction];
        required property uuid -> uuid {constraint exclusive};
        required property name -> str;
        required property currency -> str;
        property created_at -> datetime;
    }

    type Transaction {
        required link account -> Account {
            on target delete delete source;
        };
        link category -> Category;
        required property uuid -> uuid {constraint exclusive};
        required property time -> datetime;
        required property counterparty_name -> str;
        required property amount -> float32;
        property reference -> str;
    }

    type CategoryGroup {
        required property name -> str {constraint exclusive};
        multi link categories := .<category_group[is Category];
    }

    type Category {
        required property name -> str {constraint exclusive};
        link category_group -> CategoryGroup;
        multi link transactions := .<category[is Transaction];
    }
}