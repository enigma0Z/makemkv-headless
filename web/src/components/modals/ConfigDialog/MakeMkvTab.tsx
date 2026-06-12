import { ConfigTextField } from "@/components/fields/config/ConfigTextField"
import { Link } from "@mui/material"

export const MakeMkvTab = () => {

  return <>
    <ConfigTextField
      configItem="makemkvcon_path"
      label="Path to makemkvcon"
    />
    <ul>
      <li>
        <Link href="https://www.makemkv.com">Get MakeMKV</Link> (<Link href="https://forum.makemkv.com/forum/viewtopic.php?f=3&t=224">for Linux</Link>)
      </li>
      <li>
        <Link href="https://www.makemkv.com/buy/">Purchase a license for MakeMKV</Link>
      </li>
    </ul>
  </>
}