import { Box, Button, Dialog, IconButton, Tab, Tabs, TextField, Typography } from "@mui/material"

import RefreshIcon from '@mui/icons-material/Refresh';
import CloseIcon from '@mui/icons-material/Close';
import { useGetConfigQuery, usePutConfigMutation, useReloadConfigMutation } from "@/api/v1/config/api";
import { useState } from "react";
import type { Config } from "@/api/v1/config/types";
import { ConfigDialogActions, ConfigDialogContent, ConfigDialogTitle, StyledTabContent } from "./index.styles";
import { AllConfigValuesTab } from "./LegacyTab";

type Props = {
  open: boolean
  onClose?: () => void
}

const a11yProps = (index: number) => {
  return {
    id: `vertical-tab-${index}`,
    'aria-controls': `vertical-tabpanel-${index}`,
  };
}

interface TabContentProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabContent = (props: TabContentProps) => {
  const { children, value, index, ...other } = props

  return (
    <div 
      role="tabpanel"
      hidden={value !== index}
      id={`vertical-tabpanel-${index}`}
      aria-labelledby={`vertical-tab-${index}`}
      {...other}
    >
      { value === index && (
        <StyledTabContent>
          {children}
        </StyledTabContent>
      )}
    </div>
  )
}

export const ConfigDialog = ({ open, onClose = () => {} }: Props) => {
  const [putConfig, _putConfigResult] = usePutConfigMutation()
  const [reloadConfig, _reloadConfigResult] = useReloadConfigMutation()

  const [currentTab, setCurrentTab] = useState(0)
  const [formData, setFormData] = useState<Partial<Config>>({})

  const { data, isLoading, isSuccess } = useGetConfigQuery()

  formData.config_file = formData?.config_file ?? data?.config_file ?? '';
  formData.source = formData?.source ?? data?.source ?? '';
  formData.destination = formData?.destination ?? data?.destination ?? '';
  formData.tmdb_token = formData?.tmdb_token ?? data?.tmdb_token ?? '';
  formData.makemkvcon_path = formData?.makemkvcon_path ?? data?.makemkvcon_path ?? '';
  // const log_level = formData?.log_level ?? data?.log_level ?? '';
  formData.log_file = formData?.log_file ?? data?.log_file ?? '';
  formData.temp_prefix = formData?.temp_prefix ?? data?.temp_prefix ?? '';
  formData.frontend = formData?.frontend ?? data?.frontend ?? '';
  formData.listen_port = formData?.listen_port ?? data?.listen_port ?? '';

  // useEffect(() => {
  //   if (!isLoading && isSuccess) {
  //     setFormFromApi(data)
  //   }
  // }, [isLoading, isSuccess])
  
  const handleClose = () => { onClose() }  
  
  const handleSave = () => { 
    putConfig(formData)
    onClose() 
  }

  const handleRefresh = () => {
    reloadConfig()
    setFormData({})
  }

  const handleChangeTab = (_event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue)
  }

  return <Dialog fullScreen open={open} onClose={handleClose}>
    <ConfigDialogTitle>
      <IconButton onClick={handleRefresh}><RefreshIcon /></IconButton>
      <Typography variant="h4">Settings</Typography>
      <IconButton onClick={handleClose}><CloseIcon /></IconButton>
    </ConfigDialogTitle>
    <ConfigDialogContent>
      <Tabs
        orientation="vertical"
        variant="scrollable"
        value={currentTab}
        onChange={handleChangeTab}
        sx={{ borderRight: 1, borderColor: 'divider'}}
      >
        <Tab label="File Paths" {...a11yProps(0)} />
        <Tab label="Server Settings" {...a11yProps(1)} />
        <Tab label="TMDB" {...a11yProps(2)} />
        <Tab label="MakeMKV" {...a11yProps(3)} />
        <Tab label="All Config Values" {...a11yProps(4)} />
      </Tabs>
      <TabContent index={0} value={currentTab}>
        <Typography>Tab Two!</Typography>
      </TabContent>
      <TabContent index={4} value={currentTab}>
        <AllConfigValuesTab formData={formData} setFormData={setFormData} />
      </TabContent>
    </ConfigDialogContent>
    <ConfigDialogActions>
      <Button onClick={handleClose}>Cancel</Button>
      <Button onClick={handleSave} variant="contained">Save</Button>
    </ConfigDialogActions>
  </Dialog>
}