export type StatusItem = {
  data: {
    target: string;
    text: string;
    type: string;
    raw: string;
  }
}

export type StatusResponse = {
  messages: StatusItem[]
}