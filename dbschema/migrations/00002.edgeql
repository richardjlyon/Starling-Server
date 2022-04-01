CREATE MIGRATION m1jq74awheplkmovuax5fuxrflw2hf5menvqpwvfecggiffsgjinia
    ONTO m1wirdluqcbzb5dbxgyxvtzwkd6vwjitee23cacrz73djibwq66huq
{
  ALTER TYPE default::CategoryGroup {
      ALTER PROPERTY name {
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
