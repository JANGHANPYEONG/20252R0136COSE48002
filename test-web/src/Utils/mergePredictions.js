// oldData: 배열 또는 { data: [] }도 대응
export function mergePredictions(oldData, preds, attachKey = 'prediction') {
  if (!oldData || !preds) return oldData;
  const predMap = new Map(preds.map(p => [p.id, p]));

  const mergeRows = (rows) =>
    rows.map(r => predMap.has(r.id) ? { ...r, [attachKey]: predMap.get(r.id) } : r);

  if (Array.isArray(oldData)) return mergeRows(oldData);
  if (Array.isArray(oldData.data)) return { ...oldData, data: mergeRows(oldData.data) };
  return oldData;
}
