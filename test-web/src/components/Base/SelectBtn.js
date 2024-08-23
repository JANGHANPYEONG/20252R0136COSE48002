import { Button } from '@mui/material';
import style from './style/selectbtnstyle';

const SelectedBtn = ({ date }) => {
  return (
    <Button variant="contained" value="week" style={style.button}>
      {date}
    </Button>
  );
};

const UnSelectedBtn = ({ date, handleDr }) => {
  return (
    <Button
      variant="outlined"
      value="week"
      style={style.button}
      onClick={handleDr}
    >
      {date}
    </Button>
  );
};

export { SelectedBtn, UnSelectedBtn };
