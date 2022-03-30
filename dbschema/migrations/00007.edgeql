CREATE MIGRATION m1f73vi5soy6tpnxf5gu44g7vatrak22dxudsxakudgobshvt5nbmq
    ONTO m17r5p6h2ecfdvfgyfl7toshc57rnwtnt3a2u3wxt3wmryucbchgga
{
  ALTER TYPE default::Counterparty {
      ALTER PROPERTY display_name {
          RENAME TO displayname;
      };
  };
  ALTER TYPE default::DisplayNameMap {
      ALTER PROPERTY display_name {
          RENAME TO displayname;
      };
  };
};
