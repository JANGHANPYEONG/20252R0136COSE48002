import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  TextField,
} from '@mui/material';
import { rawField, rawDBFieldToSematicWord } from '../constants/infofield';

const RawTable = ({ data, edited, handleRawInputChange }) => {
  return (
    <TableContainer
      key="rawmeat"
      component={Paper}
      sx={{ width: 'fitContent', overflow: 'auto' }}
    >
      <Table sx={{ minWidth: 300 }} size="small" aria-label="a dense table">
        <TableBody>
          {rawField.map((f, idx) => {
            return (
              <TableRow key={'raw-Row' + idx}>
                <TableCell key={'raw-' + idx + 'col1'}>
                  {rawDBFieldToSematicWord[f]}
                </TableCell>
                <TableCell key={'raw-' + idx + 'col2'}>
                  {edited ? (
                    <TextField
                      name={f}
                      value={data[f] || ''}
                      onChange={(e) => handleRawInputChange(e, f)}
                      variant="outlined"
                      size="small"
                    />
                  ) : (
                    data[f] || ''
                  )}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default RawTable;
