module default {
    type Bank {
        required property name -> str {constraint exclusive};

        multi link accounts := .<bank[is Account];
    }

    type Account {
        required property uuid -> uuid {constraint exclusive};
        required property name -> str;
        required property currency -> str;
        property created_at -> datetime;

        required link bank -> Bank {
            on target delete delete source;
        };
        multi link transactions := .<account[is Transaction];
    }

    type Counterparty {

        required property uuid -> uuid {constraint exclusive};
        required property name -> str;
        property display_name -> str;

        multi link transactions := .<counterparty[is Transaction];
    }

    type DisplayNameMap {

         property fragment -> str {constraint exclusive};
         property display_name -> str;
    }

    type Transaction {
        required link account -> Account {
            on target delete delete source;
        };
        required link counterparty -> Counterparty {
            on target delete delete source;
        };
        link category -> Category;

        required property uuid -> uuid {constraint exclusive};
        required property time -> datetime;
        required property amount -> float32;
        property reference -> str;
    }

    type CategoryGroup {
        required property name -> str {constraint exclusive};

        multi link categories := .<category_group[is Category];
    }

    type Category {
        required property uuid -> uuid {constraint exclusive};
        required property name -> str {constraint exclusive};

        link category_group -> CategoryGroup;
        multi link transactions := .<category[is Transaction];
    }
}