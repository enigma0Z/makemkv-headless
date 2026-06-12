import { Button, Dialog, IconButton, Tab, Tabs, Typography } from "@mui/material"

import RefreshIcon from '@mui/icons-material/Refresh';
import CloseIcon from '@mui/icons-material/Close';
import { usePutConfigMutation, useReloadConfigMutation } from "@/api/v1/config/api";
import { useState } from "react";
import { ConfigDialogActions, ConfigDialogContent, ConfigDialogTitle, StyledTabContent } from "./index.styles";
import { AllConfigValuesTab } from "./AllConfigValuesTab";
import { useAppSelector } from "@/api";
import { RippingPathsTab } from "./RippingPathsTab";
import { ServerSettingsTab } from "./ServerSettingsTab";
import { TmdbTab } from "./TmdbTab";
import { MakeMkvTab } from "./MakeMkvTab";

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
      style={{width: "100%"}}
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

  const config = useAppSelector(state => state.config)

  const handleClose = () => { onClose() }  
  
  const handleSave = () => { 
    putConfig(config)
    onClose() 
  }

  const handleRefresh = () => {
    reloadConfig()
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
        <Tab label="Ripping Paths" {...a11yProps(0)} />
        <Tab label="Server Settings" {...a11yProps(1)} />
        <Tab label="TMDB" {...a11yProps(2)} />
        <Tab label="MakeMKV" {...a11yProps(3)} />
        <Tab label="All Config Values" {...a11yProps(4)} />
      </Tabs>
      <TabContent index={0} value={currentTab}>
        <RippingPathsTab />
      </TabContent>
      <TabContent index={1} value={currentTab}>
        <ServerSettingsTab />
      </TabContent>
      <TabContent index={2} value={currentTab}>
        <TmdbTab />
      </TabContent>
      <TabContent index={3} value={currentTab}>
        <MakeMkvTab />
      </TabContent>
      <TabContent index={4} value={currentTab}>
        <AllConfigValuesTab />
      </TabContent>
    </ConfigDialogContent>
    <ConfigDialogActions>
      <Button onClick={handleClose}>Cancel</Button>
      <Button onClick={handleSave} variant="contained">Save</Button>
    </ConfigDialogActions>
  </Dialog>
}