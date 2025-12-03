import { apiIP } from '../../config';

export const deploySpectralModel = async () => {
  const data = await fetch(`${apiIP}/train/model`).then((res) => res.json());

  // HATEOAS link
  const deployLink = data._links?.train.deploy.href;
  const deployMethod = data._links?.train.deploy.method;

  // debug
  console.log('Deploy link:', deployLink);
  console.log('Deploy method:', deployMethod);
  if (!deployLink) {
    throw new Error('Train link not found in response');
  }

  return fetch(deployLink, {
    method: deployMethod,
    headers: {
      'Content-Type': 'application/json',
    },
    // modelId
    body: JSON.stringify(),
  });
};

export default deploySpectralModel;
