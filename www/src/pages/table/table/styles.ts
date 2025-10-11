/** Table styles applied to all tables */
export const tableStyles = {
  width: "100%",
  "& div.ant-table-container": {
    border: "1px solid #bbb",
    borderRadius: 4,
    borderLeft: "1px solid #bbb !important",
  },
  "& div.ant-table-content": {
    width: "100%",
    overflowX: "scroll" as "scroll",
  },
  "& div.ant-card-body": {
    paddingLeft: 0,
    paddingRight: 0,
  },
  "& th": {
    fontWeight: 600,
  },
  "& .ant-table-cell": {
    verticalAlign: "top",
  },
  "& .column-datatype": {
    fontWeight: "normal",
  },
};
