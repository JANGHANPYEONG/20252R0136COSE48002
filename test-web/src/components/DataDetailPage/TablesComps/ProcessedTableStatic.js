import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  deepAgingStaticField,
  deepAgingStaticDBFieldToSemanticWord,
} from '../constants/infofield';

const ProcessedTableStatic = ({
  processedMinute,
  processedToggleValue,
  processed_data,
  processed_data_seq,
}) => {
  const len = processed_data_seq.length - 2;
  const target = processedToggleValue; //n회
  const targetIndex = processed_data_seq.indexOf(target) - 1;

  return (
    <TableContainer
      key="processedmeat"
      component={Paper}
      sx={{ minWidth: 'fitContent', maxWidth: '680px', overflow: 'auto' }}
    >
      <Table sx={{ minWidth: 300 }} size="small" aria-label="a dense table">
        <TableHead>
          <TableRow>
            <TableCell style={{ background: '#cfd8dc' }}>{}</TableCell>
            <TableCell align="right" style={{ background: '#cfd8dc' }}>
              {processedToggleValue}차
            </TableCell>
            {/* {
              // 2회차 이상부터
              Array.from({ length: len }, (_, arr_idx) => (
                <TableCell align="right" style={{ background: '#cfd8dc' }}>
                  {processed_data_seq[arr_idx + 2]}차
                </TableCell>
              ))
            } */}
          </TableRow>
        </TableHead>
        <TableBody>
          {deepAgingStaticField.map((f, idx) => (
            <TableRow
              key={'processed-' + idx}
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
            >
              <TableCell component="th" scope="row">
                {deepAgingStaticDBFieldToSemanticWord[f]}
              </TableCell>
              <TableCell align="right">
                {
                  // 1회차
                  f === 'minute'
                    ? processedMinute[targetIndex]
                      ? processedMinute[targetIndex]
                      : ''
                    : processed_data[targetIndex]?.[f]
                      ? processed_data[targetIndex]?.[f]
                      : ''
                }
              </TableCell>
              {/* {
                //2회차 부터
                Array.from({ length: len }, (_, arr_idx) => (
                  <TableCell align="right">
                    {f === 'minute'
                      ? processedMinute[arr_idx + 1]
                        ? processedMinute[arr_idx + 1]
                        : ''
                      : processed_data[arr_idx + 1]?.[f]
                        ? processed_data[arr_idx + 1]?.[f]
                        : ''}
                  </TableCell>
                ))
              } */}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default ProcessedTableStatic;
