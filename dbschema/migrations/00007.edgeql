CREATE MIGRATION m1brcmjlqfdixkhk7v2koqygo2g6vy5xr7qxvfa5lkjw6l43s7ksua
    ONTO m125de3zsfdxy3iayxmx3deg2iagjtweo34w7snzc2mq4vmjvg7l2a
{
  ALTER TYPE default::Account {
      DROP PROPERTY server_last_updated;
  };
};
