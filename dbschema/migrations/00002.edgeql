CREATE MIGRATION m1emngj5b5rfbnyarod55czd5kivhiktp2hnxaluqlm4php2t4w5ea
    ONTO m15hi4lqboaqvz27czzp5b6frncoq34gszprq4d5rwi7ihliisp3fq
{
  ALTER TYPE default::Account {
      ALTER PROPERTY bank_name {
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
