export type SortInfo = {
  name?: string;
  id?: string;
  main_indexes: number[];
  extra_indexes: number[];
  split_segments?: number[];
  id_db?: string;
}

export type ShowInfo = {
  season_number?: number;
  first_episode?: number;
}