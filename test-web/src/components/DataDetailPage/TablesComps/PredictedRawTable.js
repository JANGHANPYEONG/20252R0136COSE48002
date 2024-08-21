import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { rawPAField, rawPADBFieldToSematicWord } from '../constants/infofield';

const PredictedRawTable = ({ raw_data, dataPA }) => {
  return (
    <TableContainer
      key="rawmeat"
      component={Paper}
      sx={{ width: 'fitContent', overflow: 'auto', marginTop: '40px' }}
    >
      <Table sx={{ minWidth: 300 }} size="small" aria-label="a dense table">
        <TableBody>
          {rawPAField.map((f, idx) => {
            return (
              <TableRow key={'raw-Row' + idx}>
                <TableCell key={'raw-' + idx + 'col1'}>
                  {rawPADBFieldToSematicWord[f]}
                </TableCell>
                <TableCell key={'raw-' + idx + 'col2'}>
                  <div>
                    {dataPA
                      ? f === 'xai_gradeNum'
                        ? dataPA['xai_gradeNum'] === 0
                          ? '0'
                          : dataPA[f]
                        : dataPA[f]
                          ? dataPA[f].toFixed(2)
                          : ''
                      : ''}
                  </div>

                  {
                    // 오차 계산
                    f !== 'xai_gradeNum' && (
                      <div style={{ marginLeft: '10px' }}>
                        {dataPA ? (
                          dataPA[f] ? (
                            <span
                              style={
                                dataPA[f].toFixed(2) - raw_data[f] > 0
                                  ? { color: 'red' }
                                  : { color: 'blue' }
                              }
                            >
                              {dataPA[f].toFixed(2) - raw_data[f] > 0
                                ? '(+' +
                                  (dataPA[f].toFixed(2) - raw_data[f]).toFixed(
                                    2
                                  ) +
                                  ')'
                                : '(' +
                                  (dataPA[f].toFixed(2) - raw_data[f]).toFixed(
                                    2
                                  ) +
                                  ')'}
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
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default PredictedRawTable;
