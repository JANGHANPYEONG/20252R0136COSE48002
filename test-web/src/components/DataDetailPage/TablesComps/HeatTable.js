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
  heatedField,
  heatedDBFieldToSemanticWord,
} from '../constants/infofield';

const HeatTable = ({
  edited,
  heatInput,
  heated_data,
  heatedToggleValue,
  handleInputChange,
  processed_data_seq,
}) => {
  const len = processed_data_seq.length - 1;
  return (
    <TableContainer
      key="heatedmeat"
      component={Paper}
      sx={{ width: '100%', maxHeight: '47vh', overflow: 'auto' }}
    >
      <Table sx={{ minWidth: 300 }} size="small" aria-label="a dense table">
        <TableHead>
          <TableRow key={'heatedmeat-explanation'}>
            <TableCell key={'heatedmeat-exp-col'}>{}</TableCell>
            <TableCell key={'heatedmeat-exp-col0'}>원육</TableCell>
            {Array.from({ length: len }, (_, arr_idx) => (
              <TableCell key={'heatedmeat-exp-col' + (arr_idx + 1)}>
                {processed_data_seq[arr_idx + 1]}차
              </TableCell>
            ))}
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
                  {edited ? (
                    <input
                      key={'heated-' + idx + 'input'}
                      style={{ width: '100px', height: '23px' }}
                      name={f}
                      value={heatInput[0]?.[f]}
                      placeholder={
                        heated_data[0] === null ? '0.0' : heated_data[0]?.[f]
                      }
                      onChange={(e) => {
                        handleInputChange(e, 2, 0);
                      }}
                    />
                  ) : heatInput[0]?.[f] ? (
                    heatInput[0]?.[f]
                  ) : (
                    ''
                  )}
                </TableCell>
                {
                  // 실험실 및 가열육 추가 데이터 수정
                  Array.from({ length: len }, (_, arr_idx) => (
                    <TableCell key={'heated-' + arr_idx + '-col' + arr_idx}>
                      {edited ? (
                        <input
                          key={'heated-' + arr_idx + '-input'}
                          style={{ width: '100px', height: '23px' }}
                          name={f}
                          value={heatInput[arr_idx + 1]?.[f]}
                          placeholder={
                            heated_data[arr_idx + 1] === null
                              ? '0.0'
                              : heated_data[arr_idx]?.[f]
                          }
                          onChange={(e) => {
                            handleInputChange(e, 2, arr_idx + 1);
                          }}
                        />
                      ) : heatInput[arr_idx + 1]?.[f] ? (
                        heatInput[arr_idx + 1]?.[f]
                      ) : (
                        ''
                      )}
                    </TableCell>
                  ))
                }
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default HeatTable;
