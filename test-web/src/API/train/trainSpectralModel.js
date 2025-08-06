import { apiIP } from '../../config';

export const trainSpectralModel = async (trainDataSet) => {
  const data = await fetch(`${apiIP}/train/model`).then((res) => res.json());

  // HATEOAS link
  const trainLink = data._links?.train.href;
  const trainMethod = data._links?.train.method;

  // debug
  console.log('Train link:', trainLink);
  console.log('Train method:', trainMethod);
  if (!trainLink) {
    throw new Error('Train link not found in response');
  }

  return fetch(trainLink, {
    method: trainMethod,
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(trainDataSet),
  });
};

export default trainSpectralModel;
