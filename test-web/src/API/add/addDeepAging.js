import { apiIP} from "../../config";

export const addDeepAgingRegister = async (req) =>{
    const response = await fetch(`http://${apiIP}/meat/add/deep-aging-data`,{
        method: 'POST',
        headers:{
            'Content-Type' : 'application/json',
        },
        body: JSON.stringify(req),
    });
    return response;
}

export default addDeepAgingRegister