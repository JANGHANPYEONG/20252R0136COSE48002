import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';

const HeatTableStatic = ({ heated_data, heatedToggleValue }) => {
  return (
    <TableContainer
      key="heatedmeat"
      component={Paper}
      sx={{ width: '100%', overflow: 'auto' }}
    >
      <Table sx={{ minWidth: 300 }} size="small" aria-label="a dense table">
        <TableHead>
          <TableRow key={'heatedmeat-explanation'}>
            <TableCell key={'heatedmeat-exp-col'}>{}</TableCell>
            <TableCell key={'heatedmeat-exp-col0'}>원육</TableCell>
            {Array.from(
              { length: Number(heatedToggleValue.slice(0, -1)) },
              (_, arr_idx) => (
                <TableCell key={'heatedmeat-exp-col' + (arr_idx + 1)}>
                  {arr_idx + 1}회차
                </TableCell>
              )
            )}
          </TableRow>
        </TableHead>
        <TableBody>
          {heatedField.map((f, idx) => {
            return (
              <TableRow key={'heated-' + idx}>
                <TableCell key={'heated-' + idx + 'col1'}>
                  {heatedDBFieldToSemanticWord[f]}
                </TableCell>
                <TableCell key={'heated-' + idx + 'col2'}>
                  {heated_data[0]?.[f] ? heated_data[0]?.[f] : ''}
                </TableCell>
                {
                  // 실험실 및 가열육 추가 데이터
                  Array.from(
                    { length: Number(heatedToggleValue.slice(0, -1)) },
                    (_, arr_idx) => (
                      <TableCell key={'heated-' + arr_idx + '-col' + arr_idx}>
                        {heated_data[arr_idx + 1]?.[f]
                          ? heated_data[arr_idx + 1]?.[f]
                          : ''}
                      </TableCell>
                    )
                  )
                }
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default HeatTableStatic;

const heatedField = [
  'flavor',
  'juiciness',
  'tenderness',
  'umami',
  'palability',
];
const heatedDBFieldToSemanticWord = {
  flavor: '풍미',
  juiciness: '육즙',
  tenderness: '연도',
  umami: '감칠맛',
  palability: '기호도',
};
