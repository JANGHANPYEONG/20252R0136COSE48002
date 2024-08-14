import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { labField, labDBFieldToSemanticWord } from '../constants/infofield';
const LabTable = ({
  edited,
  labInput,
  lab_data,
  labToggleValue,
  handleInputChange,
  processed_data_seq,
}) => {
  const len = processed_data_seq.length - 1;
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
            {Array.from({ length: len }, (_, arr_idx) => (
              <TableCell key={'labData-exp-col' + (arr_idx + 1)}>
                {' '}
                {processed_data_seq[arr_idx + 1]}차{' '}
              </TableCell>
            ))}
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
                  {edited ? (
                    <input
                      key={'lab-' + idx + 'input'}
                      style={{ width: '100px', height: '23px' }}
                      name={f}
                      value={labInput[0]?.[f]}
                      placeholder={
                        lab_data[0] === null ? '0.0' : lab_data[0]?.[f]
                      }
                      onChange={(e) => {
                        handleInputChange(e, 3, 0);
                      }}
                    />
                  ) : labInput[0]?.[f] ? (
                    labInput[0]?.[f]
                  ) : (
                    ''
                  )}
                </TableCell>
                {
                  // 실험실 및 가열육 추가 데이터 수정
                  Array.from({ length: len }, (_, arr_idx) => (
                    <TableCell key={'lab-' + arr_idx + '-col' + arr_idx}>
                      {edited ? (
                        <input
                          key={'lab-' + arr_idx + '-input'}
                          style={{ width: '100px', height: '23px' }}
                          name={f}
                          value={labInput[arr_idx + 1]?.[f]}
                          placeholder={
                            lab_data[arr_idx + 1] === null
                              ? '0.0'
                              : lab_data[arr_idx]?.[f]
                          }
                          onChange={(e) => {
                            handleInputChange(e, 3, arr_idx + 1);
                          }}
                        />
                      ) : labInput[arr_idx + 1]?.[f] ? (
                        labInput[arr_idx + 1]?.[f]
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

export default LabTable;
