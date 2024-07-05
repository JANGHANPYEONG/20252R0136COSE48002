import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';

const ApiTable = ({ api_data }) => {
  return (
    <TableContainer
      key="api"
      component={Paper}
      sx={{ width: 'fitContent', overflow: 'auto' }}
    >
      <Table sx={{ minWidth: 300 }} size="small" aria-label="a dense table">
        <TableHead></TableHead>
        <TableBody>
          {apiField.map((f, idx) => {
            return (
              <TableRow key={'api-' + idx}>
                <TableCell key={'api-' + idx + 'col1'}>
                  {apiDBFieldToSemanticWord[f]}
                </TableCell>
                <TableCell key={'api-' + idx + 'col2'}>
                  {api_data[f] ? api_data[f] : ''}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default ApiTable;

const apiField = [
  'birthYmd',
  'butcheryYmd',
  'farmAddr',
  'farmerNm',
  'gradeNm',
  'primalValue',
  'secondaryValue',
  'sexType',
  'species',
  'statusType',
  'traceNum',
];
const apiDBFieldToSemanticWord = {
  birthYmd: '출생년월일',
  butcheryYmd: '도축일자',
  farmAddr: '사육지',
  farmerNm: '소유주',
  gradeNm: '육질등급',
  primalValue: '대분류',
  secondaryValue: '소분류',
  sexType: '성별',
  species: '종',
  statusType: '데이터승인',
  traceNum: 'traceNum',
};
