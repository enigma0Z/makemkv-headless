export type Response<T> = {
  status: (
    'success' |
    'failure' |
    'started' |
    'in progress' |
    'done' |
    'stopped' |
    'error'
  ),
  data: T
}