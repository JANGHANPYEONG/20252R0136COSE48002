import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';

import { apiField, apiDBFieldToSemanticWord } from '../constants/infofield';

const ApiTable = ({ api_data }) => {
  return (
    <TableContainer
      key="api"
      component={Paper}
      sx={{ width: 'fitContent', overflow: 'auto' }}
    >
      <Table sx={{ minWidth: 300 }} size="small" aria-label="a dense table">
        <TableHead></TableHead>
        <TableBody>
          {apiField.map((f, idx) => {
            return (
              <TableRow key={'api-' + idx}>
                <TableCell key={'api-' + idx + 'col1'}>
                  {apiDBFieldToSemanticWord[f]}
                </TableCell>
                <TableCell key={'api-' + idx + 'col2'}>
                  {api_data[f] ? api_data[f] : ''}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default ApiTable;


