import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { labStaticField, labStaticDBFieldToSemanticWord } from '../constants/infofield';

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
          {labStaticField.map((f, idx) => {
            return (
              <TableRow key={'lab-' + idx}>
                <TableCell key={'lab-' + idx + 'col1'}>
                  {labStaticDBFieldToSemanticWord[f]}
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

