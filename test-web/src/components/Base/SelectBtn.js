import { Button } from '@mui/material';

const SelectedBtn = ({ date }) => {
  return (
    <Button variant="contained" value="week" style={styles.button}>
      {date}
    </Button>
  );
};

const UnSelectedBtn = ({ date, handleDr }) => {
  return (
    <Button
      variant="outlined"
      value="week"
      style={styles.button}
      onClick={handleDr}
    >
      {date}
    </Button>
  );
};

export { SelectedBtn, UnSelectedBtn };

const styles = {
  button: {
    borderRadius: '50px',
    padding: '0px 15px',
    width: '70px',
    height: '35px',
    fontWeight: '500',
  },
};
