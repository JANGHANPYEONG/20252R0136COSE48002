const navy = '#0F3659';

const style = {
  button: {
    borderRadius: '50px',
    padding: '0px 15px',
    height: '30px',
    fontWeight: '500',
    backgroundColor: navy,
  },
  unClickedbutton: {
    borderRadius: '50px',
    padding: '0px 15px',
    height: '30px',
    fontWeight: '500',
    color: navy,
    border: `1px solid ${navy}`,
  },
  finishBtn: {
    color: navy,
    border: 'none',
    backgroundColor: 'white',
    fontWeight: '600',
  },
  cardStyle: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: '10px 10px',
    gap: '10px',
    gridTemplateColumns: 'minmax(400px, max-content) 1fr',
    width: 'fit-content',
    minWidth: '500px',
    height: 'fit-content',
    borderRadius: '10px',
  },
};

export default style;
