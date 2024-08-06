import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
// modal component
import InputTransitionsModal from '../InputTransitionsModal';

const ProcessedTable = ({
  edited,
  modal,
  setModal,
  processed_img_path,
  processedMinute,
  setProcessedMinute,
  processedInput,
  processedToggleValue,
  handleInputChange,
  processed_data,
  processed_date,
}) => {
  // 처리육 딥에이징 시간 (분) input 핸들링
  const handleMinuteInputChange = (e, index) => {
    const value = e.target.value;
    if (!isNaN(+value)) {
      setProcessedMinute((prev) => ({ ...prev, [index]: value }));
    }
  };

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
              1회차
            </TableCell>
            {
              // 2회차 이상부터
              Array.from(
                { length: Number(processedToggleValue.slice(0, -1)) - 1 },
                (_, arr_idx) => (
                  <TableCell align="right" style={{ background: '#cfd8dc' }}>
                    {arr_idx + 2}회차
                  </TableCell>
                )
              )
            }
          </TableRow>
        </TableHead>
        <TableBody>
          {deepAgingField.map((f, idx) => (
            <TableRow
              key={'processed-' + idx}
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
            >
              <TableCell component="th" scope="row">
                {deepAgingDBFieldToSemanticWord[f]}
              </TableCell>
              <TableCell align="right">
                {
                  // 1회차
                  f === 'minute' ? (
                    // minute값을 업로드하는 경우 (수정 불가 , 추가할 때 입력만 가능) -> 이미지 업로드 부분만 보면 될 것 같은데 수정 api 다 잘됨
                    edited &&
                    (processed_img_path[0] === null ||
                      processed_img_path === null) ? (
                      modal ? (
                        <InputTransitionsModal setModal={setModal} />
                      ) : (
                        <input
                          key={'processed-' + idx + 'input'}
                          style={{ width: '100px', height: '23px' }}
                          name={f}
                          value={processedMinute[0]}
                          placeholder={
                            processedMinute[0] === null
                              ? '0.0'
                              : processedMinute[0]
                          }
                          onChange={(e) => {
                            handleMinuteInputChange(e, 0);
                          }}
                        />
                      )
                    ) : processedMinute[0] ? (
                      processedMinute[0]
                    ) : (
                      ''
                    )
                  ) : // createdAt seqno period 수정 X (자동 수정됨)
                  f === 'seqno' || f === 'period' ? (
                    processedInput[0]?.[f] ? (
                      processedInput[0]?.[f]
                    ) : (
                      ''
                    )
                  ) : f === 'createdAt' ? (
                    processed_date[0] ? (
                      processed_date[0]
                    ) : (
                      ''
                    )
                  ) : //나머지 데이터 (이미지 업로드 후에만 수정 가능 )
                  edited ? (
                    modal ? (
                      <InputTransitionsModal setModal={setModal} />
                    ) : (
                      <input
                        key={'processed-' + idx + 'input'}
                        style={{ width: '100px', height: '23px' }}
                        name={f}
                        value={processedInput[0]?.[f]}
                        placeholder={
                          processed_data[0] === null
                            ? '0.0'
                            : processed_data[0]?.[f]
                        }
                        onChange={(e) => {
                          handleInputChange(e, 1, 0);
                        }}
                      />
                    )
                  ) : processedInput[0]?.[f] ? (
                    processedInput[0]?.[f]
                  ) : (
                    ''
                  )
                }
              </TableCell>
              {
                //2회차 부터
                Array.from(
                  { length: Number(processedToggleValue.slice(0, -1)) - 1 },
                  (_, arr_idx) => (
                    <TableCell align="right">
                      {f === 'minute' ? (
                        edited ? (
                          modal ? (
                            <InputTransitionsModal setModal={setModal} />
                          ) : (
                            <input
                              key={'processed-' + idx + 'input'}
                              name={f}
                              style={{ width: '100px', height: '23px' }}
                              value={processedMinute[arr_idx + 1]}
                              placeholder={
                                processedMinute[arr_idx + 1] === null
                                  ? '0.0'
                                  : processedMinute[arr_idx + 1]
                              }
                              onChange={(e) => {
                                handleMinuteInputChange(e, arr_idx + 1);
                              }}
                            />
                          )
                        ) : processedMinute[arr_idx + 1] ? (
                          processedMinute[arr_idx + 1]
                        ) : (
                          ''
                        )
                      ) : // createdAt seqno period 수정 X (자동 수정됨)
                      f === 'seqno' || f === 'period' ? (
                        processedInput[arr_idx + 1]?.[f] ? (
                          processedInput[arr_idx + 1]?.[f]
                        ) : (
                          ''
                        )
                      ) : f === 'createdAt' ? (
                        processed_date[arr_idx + 1] ? (
                          processed_date[arr_idx + 1]
                        ) : (
                          ''
                        )
                      ) : //나머지 데이터 (이미지 업로드 후에만 수정 가능 )
                      edited ? (
                        modal ? (
                          <InputTransitionsModal setModal={setModal} />
                        ) : (
                          <input
                            key={'processed-' + arr_idx + '-input'}
                            style={{ width: '100px', height: '23px' }}
                            name={f}
                            value={processedInput[arr_idx + 1]?.[f]}
                            placeholder={
                              processed_data[arr_idx + 1] === null
                                ? '0.0'
                                : processed_data[arr_idx]?.[f]
                            }
                            onChange={(e) => {
                              handleInputChange(e, 1, arr_idx + 1);
                            }}
                          />
                        )
                      ) : processedInput[arr_idx + 1]?.[f] ? (
                        processedInput[arr_idx + 1]?.[f]
                      ) : (
                        ''
                      )}
                    </TableCell>
                  )
                )
              }
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default ProcessedTable;

const deepAgingField = [
  'marbling',
  'color',
  'texture',
  'surfaceMoisture',
  'overall',
  'createdAt',
  //'seqno',
  'minute',
  'period',
];
const deepAgingDBFieldToSemanticWord = {
  marbling: '마블링',
  color: '육색',
  texture: '조직감',
  surfaceMoisture: '표면육즙',
  overall: '기호도',
  createdAt: '생성일자',
  //seqno: '딥에이징 회차',
  minute: '딥에이징 시간(분)',
  period: 'period',
};
