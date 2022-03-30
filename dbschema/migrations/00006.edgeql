CREATE MIGRATION m17r5p6h2ecfdvfgyfl7toshc57rnwtnt3a2u3wxt3wmryucbchgga
    ONTO m1r2jorkuq7d457t33u4xt7sceo7zewej4oepajxsgtiu2gjgurcvq
{
  ALTER TYPE default::DisplayNameMap {
      ALTER PROPERTY name {
          RENAME TO fragment;
      };
      DROP PROPERTY name_fragment;
  };
};
