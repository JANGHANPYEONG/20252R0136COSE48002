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
  deepAgingPAField,
  deepAgingPADBFieldToSemanticWord,
} from '../constants/infofield';

const PredictedProcessedTablePA = ({ seqno, processed_data, dataPA }) => {
  const processedDataIdx = seqno - 1;
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
              {seqno}회차
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {deepAgingPAField.map((f, idx) => (
            <TableRow
              key={'processed-' + idx}
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
            >
              <TableCell component="th" scope="row">
                {deepAgingPADBFieldToSemanticWord[f]}
              </TableCell>
              <TableCell align="right">
                <div style={{ display: 'flex' }}>
                  <div>
                    {
                      // 1회차
                      dataPA
                        ? f === 'xai_gradeNum'
                          ? dataPA['xai_gradeNum'] === 0
                            ? '0'
                            : dataPA[f]
                          : dataPA[f]
                            ? dataPA[f].toFixed(2)
                            : ''
                        : ''
                    }
                  </div>

                  {
                    // 오차 계산
                    f !== 'xai_gradeNum' && f !== 'seqno' && f !== 'period' && (
                      <div style={{ marginLeft: '10px' }}>
                        {dataPA ? (
                          dataPA[f] ? (
                            <span
                              style={
                                dataPA[f].toFixed(2) -
                                  processed_data[processedDataIdx]?.[f] >
                                0
                                  ? { color: 'red' }
                                  : { color: 'blue' }
                              }
                            >
                              {
                                dataPA[f].toFixed(2) -
                                  processed_data[processedDataIdx]?.[f] >
                                0
                                  ? '(+' +
                                    (
                                      dataPA[f].toFixed(2) -
                                      processed_data[processedDataIdx]?.[f]
                                    ).toFixed(2) +
                                    ')' /*플러스인 경우 */
                                  : '(' +
                                    (
                                      dataPA[f].toFixed(2) -
                                      processed_data[processedDataIdx]?.[f]
                                    ).toFixed(2) +
                                    ')' /*미이너스인 경우 */
                              }
                            </span>
                          ) : (
                            <span></span>
                          )
                        ) : (
                          ''
                        )}
                      </div>
                    )
                  }
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default PredictedProcessedTablePA;
