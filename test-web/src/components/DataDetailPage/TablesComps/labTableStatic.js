import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';

const LabTableStatic = ({ lab_data, labToggleValue }) => {
  return (
    <TableContainer
      key="labData"
      component={Paper}
      sx={{ maxWidth: '680px', maxHeight: '50vh', overflow: 'auto' }}
    >
      <Table sx={{ minWidth: 300 }} size="small" aria-label="a dense table">
        <TableHead>
          <TableRow key={'labData-explanation'}>
            <TableCell key={'labData-exp-col'}>{}</TableCell>
            <TableCell key={'labData-exp-col0'}>원육</TableCell>
            {Array.from(
              { length: Number(labToggleValue.slice(0, -1)) },
              (_, arr_idx) => (
                <TableCell key={'labData-exp-col' + (arr_idx + 1)}>
                  {' '}
                  {arr_idx + 1}회차{' '}
                </TableCell>
              )
            )}
          </TableRow>
        </TableHead>

        <TableBody>
          {labField.map((f, idx) => {
            return (
              <TableRow key={'lab-' + idx}>
                <TableCell key={'lab-' + idx + 'col1'}>
                  {labDBFieldToSemanticWord[f]}
                </TableCell>
                <TableCell key={'lab-' + idx + 'col2'}>
                  {lab_data[0]?.[f] ? lab_data[0]?.[f] : ''}
                </TableCell>
                {
                  // 실험실 추가 데이터
                  Array.from(
                    { length: Number(labToggleValue.slice(0, -1)) },
                    (_, arr_idx) => (
                      <TableCell key={'lab-' + arr_idx + '-col' + arr_idx}>
                        {lab_data[arr_idx + 1]?.[f]
                          ? lab_data[arr_idx + 1]?.[f]
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

export default LabTableStatic;

const labField = [
  'L',
  'a',
  'b',
  'DL',
  'CL',
  'RW',
  'ph',
  'WBSF',
  'cardepsin_activity',
  'MFI',
  'sourness',
  'bitterness',
  'umami',
  'richness',
  'Collagen',
];
const labDBFieldToSemanticWord = {
  L: '명도',
  a: '적색도',
  b: '황색도',
  DL: '육즙감량',
  CL: '가열감량',
  RW: '압착감량',
  ph: 'pH',
  WBSF: '전단가',
  cardepsin_activity: '카뎁신활성도',
  MFI: '근소편화지수',
  sourness: '신만',
  bitterness: '진한맛',
  umami: '감칠맛',
  richness: '후미',
  collagen: '콜라겐',
};
