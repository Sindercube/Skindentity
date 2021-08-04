<h1>
  <p align="center">
    <img alt="Skindentity" src="icon.png">Skindentity
  </p>

  <p align="center">
    <a href="https://go.deta.dev/deploy">
      <img alt="Latest Release" src="https://img.shields.io/badge/Deploy%20to-DETA-%23D53AA2">
    </a>
    <a href="https://heroku.com/deploy">
      <img src="https://img.shields.io/badge/Deploy%20to-Heroku-%237056BF" />
    </a>
  </p>
</h1>

Python FastAPI with a collection of Minecraft Skin rendering APIs.

## Current APIs

### `https://skindentity.deta.dev/portrait/?player=<name>`
![preview](previews/portrait.png)

### `https://skindentity.deta.dev/profile/?player=<name>`
![preview](previews/profile.png)

### Inputs

|Value|Type|Description|Required|
|-|-|-|-|
|`player`|str|Which player's skin to use|or `image_url`
|`image_url`|str|Link to get an image from|or `player`
|`slim`|bool|Render skins with slim arms|`false`

###### For an easier time figuring out how to use the API, [click here](https://skindentity.deta.dev/docs).

### Planned Inputs

|Value|Type|Description|Required|
|-|-|-|-|
|`padding`|int|How many pixels around the image to make transparent (1 to 6) (set to 2 to fit inside circles)|`false`
|`upscale`|int|What factor to upscale the image by (2 to 30)|`false`

###### Psst, want to host your own API for free? Go check out [DETA](https://www.deta.sh/), they're pretty cool.
