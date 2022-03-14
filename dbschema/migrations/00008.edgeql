CREATE MIGRATION m1jyacsypnn7t7dccefuxafizdbw6g4yyty5d7ixqoyebbxgmun2ma
    ONTO m1brcmjlqfdixkhk7v2koqygo2g6vy5xr7qxvfa5lkjw6l43s7ksua
{
  ALTER TYPE default::Bank {
      CREATE REQUIRED PROPERTY auth_token_hash -> std::str {
          SET REQUIRED USING ('NOT SET');
      };
  };
};
