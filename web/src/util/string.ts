export const hmsToSeconds = (hmsTime?: string) => {
  if (hmsTime) {
    const [seconds, minutes, hours] = hmsTime.split(":").reverse()
    let runningTime = 0

    if (seconds && parseInt(seconds)) runningTime += parseInt(seconds)
    if (minutes && parseInt(minutes)) runningTime += parseInt(minutes)*60
    if (hours && parseInt(hours))     runningTime += parseInt(hours)*60*60

    return runningTime
  } else {
    return 0
  }
}