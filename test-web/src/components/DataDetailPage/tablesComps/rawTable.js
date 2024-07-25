import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  TextField,
} from '@mui/material';

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

const rawField = ['marbling', 'color', 'texture', 'surfaceMoisture', 'overall'];
const rawDBFieldToSematicWord = {
  marbling: '마블링',
  color: '육색',
  texture: '조직감',
  surfaceMoisture: '표면육즙',
  overall: '기호도',
};
