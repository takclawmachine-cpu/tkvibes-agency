import { useRef, useMemo, useEffect, useState, useCallback } from 'react'
import { useFrame, extend, useThree } from '@react-three/fiber'
import { shaderMaterial, Text } from '@react-three/drei'
import * as THREE from 'three'
import { motion } from 'framer-motion'

// Custom atmosphere shader material
const AtmosphereMaterial = shaderMaterial(
  { glowColor: new THREE.Color(0x5eead4), c: 0.3, p: 4.0 },
  `varying vec3 vNormal;
   void main() {
     vNormal = normalize(normalMatrix * normal);
     gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
   }`,
  `uniform vec3 glowColor;
   uniform float c;
   uniform float p;
   varying vec3 vNormal;
   void main() {
     float intensity = pow(c - dot(vNormal, vec3(0.0, 0.0, 1.0)), p);
     gl_FragColor = vec4(glowColor * intensity, intensity);
   }`
)
extend({ AtmosphereMaterial })

// Portfolio data from tkvibes.in
const PORTFOLIO = [
  { name: "Let's Smile Dental", category: "Healthcare", image: "https://tkvibes.in/websites/screenshots/lets-smile-dental.png" },
  { name: "Tasty Bites Cafe", category: "Food & Beverage", image: "https://tkvibes.in/websites/screenshots/tasty-bites-3d-cafe.png" },
  { name: "Deep Water Tank", category: "Service Business", image: "https://tkvibes.in/websites/screenshots/deep-water-tank-cleaning-modern.png" },
  { name: "Mita Dental Clinic", category: "Healthcare", image: "https://tkvibes.in/websites/screenshots/mita-dental-website.png" },
  { name: "Multi-Specialty Dental", category: "Healthcare", image: "https://tkvibes.in/websites/screenshots/dental-clinic-3d.png" }
]

// City coordinates for globe
const CITIES = [
  [40.7,-74],[34,-118],[51.5,0],[48.9,2.3],[52.5,13.4],[35.7,139.7],[22.3,114.2],[1.3,103.8],
  [28.6,77.2],[-33.9,151.2],[37.6,127],[31.2,121.5],[23.1,113.3],[41,29],[39.9,116.4],[55.8,37.6],
  [30,31.2],[19.1,72.9],[25,55.3],[-23,-43.2],[19.4,-99.1],[-12,-77],[33.6,-7.6],[14.6,121],
  [13.7,100.5],[3.1,101.7],[37.6,55.3],[24.7,46.7],[41.7,44.8],[6.5,3.4],[-26,28],[9,38.7],
  [38.9,-77],[43.6,-79.4],[47.6,-122],[29.8,-95.4],[25.8,-80.2],[40.4,-3.7],[41.4,2.2],[59.9,10.7],
  [60.2,25],[55.7,12.6],[50.4,30.5],[36.8,10.2],[-1.3,36.8],[-6.2,106.8],[21,105.8],[16.9,82.2],
  [26.9,75.8],[9.9,76.3],[23,72.6],[13.1,77.6],[19.1,72.9],[33.3,44.4],[27.7,85.3]
]

// Continent paths from tkvibes.in
const CONTINENTS = [
  [[72,-170],[68,-165],[64,-140],[60,-139],[58,-148],[60,-152],[63,-165],[65,-168],[70,-165],[72,-170]],
  [[60,-139],[57,-135],[55,-130],[50,-127],[48,-124],[42,-124],[37,-122],[33,-118],[30,-115],[28,-105],[26,-98],[25,-90],[29,-85],[30,-82],[27,-80],[25,-80],[27,-77],[30,-82],[35,-76],[40,-74],[42,-70],[44,-68],[46,-64],[48,-59],[50,-57],[53,-56],[55,-60],[58,-63],[60,-64]],
  [[60,-64],[62,-75],[58,-80],[55,-83],[50,-88],[48,-88],[48,-95],[52,-97],[55,-100],[58,-110],[60,-120],[60,-139]],
  [[12,-73],[10,-72],[8,-68],[7,-63],[5,-57],[4,-53],[2,-50],[0,-50],[-2,-44],[-5,-35],[-8,-35],[-10,-37],[-13,-38],[-17,-39],[-22,-41],[-25,-46],[-28,-49],[-32,-52],[-35,-57],[-38,-58],[-40,-62],[-43,-65],[-46,-67],[-50,-73],[-53,-70],[-55,-68],[-52,-70],[-47,-74],[-42,-73],[-38,-63],[-34,-58],[-30,-50],[-25,-48],[-22,-43],[-20,-40],[-17,-39],[-13,-38],[-8,-35],[-5,-35],[-2,-44],[0,-50],[2,-50],[4,-53],[5,-57],[7,-63],[8,-68],[10,-72],[12,-73]],
  [[37,-10],[36,-5],[35,0],[33,10],[32,32],[30,33],[27,34],[22,37],[18,41],[15,42],[12,44],[10,45],[8,43],[5,42],[2,42],[0,42],[-3,40],[-7,40],[-10,40],[-13,40],[-17,37],[-20,35],[-25,33],[-28,32],[-30,30],[-34,26],[-35,20],[-34,18],[-30,17],[-25,15],[-20,12],[-15,12],[-10,14],[-5,10],[0,10],[5,8],[5,2],[5,-2],[7,-8],[10,-15],[14,-17],[18,-17],[21,-17],[25,-15],[30,-10],[35,-5],[37,-10]],
  [[70,20],[68,25],[65,28],[63,30],[60,30],[58,28],[56,24],[55,21],[54,14],[53,10],[52,7],[51,4],[50,2],[48,0],[47,-2],[44,-5],[43,-9],[37,-8],[36,-6],[37,0],[38,5],[39,8],[40,10],[42,13],[43,16],[44,14],[45,14],[47,15],[48,17],[50,20],[52,18],[54,16],[55,13],[56,12],[57,10],[59,10],[60,10],[62,15],[64,15],[66,16],[68,18],[70,20]],
  [[70,30],[70,60],[68,70],[65,80],[63,90],[60,100],[58,110],[55,120],[53,130],[50,135],[48,140],[45,142],[43,145],[40,140],[38,135],[35,130],[33,128],[30,122],[28,120],[25,120],[22,115],[20,110],[18,108],[15,108],[12,108],[10,106],[8,105],[5,105],[2,104],[0,104],[-2,105],[-5,106],[-8,115],[-7,120],[-5,120],[0,118],[3,115],[5,110],[8,108],[10,106],[12,100],[15,100],[18,98],[20,95],[22,90],[25,88],[28,85],[30,80],[32,75],[30,70],[28,65],[25,62],[25,58],[28,55],[30,50],[33,48],[35,45],[38,43],[40,43],[42,40],[45,38],[48,40],[50,45],[52,50],[55,55],[58,60],[60,65],[63,70],[65,75],[68,80],[70,80],[72,75],[73,60],[72,45],[70,30]],
  [[-12,131],[-14,127],[-17,123],[-20,118],[-24,115],[-28,114],[-32,115],[-35,117],[-37,140],[-38,145],[-37,150],[-34,151],[-30,153],[-26,153],[-22,150],[-19,147],[-16,145],[-14,142],[-13,137],[-12,131]],
  [[78,-72],[76,-68],[73,-56],[72,-52],[70,-52],[68,-54],[65,-54],[62,-50],[60,-45],[60,-48],[63,-52],[65,-54],[68,-56],[70,-56],[72,-55],[74,-60],[76,-68],[78,-72]]
]

function latLonToXY(lat, lon, r) {
  const phi = lat * Math.PI / 180
  const lam = lon * Math.PI / 180
  return [512 + r * Math.cos(phi) * Math.cos(lam), 512 - r * Math.sin(phi)]
}

export default function Globe3D() {
  const globeRef = useRef()
  const atmosphereRef = useRef()
  const wireframeRef = useRef()
  const cityGroupRef = useRef()
  const orbitGroupRef = useRef()
  const starsRef = useRef()
  const { viewport } = useThree()

  // Create globe texture canvas
  const globeTexture = useMemo(() => {
    const canvas = document.createElement('canvas')
    canvas.width = 1024
    canvas.height = 1024
    const ctx = canvas.getContext('2d')

    // Base ocean gradient
    const grd = ctx.createRadialGradient(512, 512, 0, 512, 512, 512)
    grd.addColorStop(0, '#0a2040')
    grd.addColorStop(1, '#051020')
    ctx.fillStyle = grd
    ctx.fillRect(0, 0, 1024, 1024)

    // Continents
    ctx.fillStyle = 'rgba(94, 234, 212, 0.45)'
    ctx.strokeStyle = 'rgba(94, 234, 212, 0.65)'
    ctx.lineWidth = 1.5

    const texR = 420
    CONTINENTS.forEach(cont => {
      ctx.beginPath()
      const first = latLonToXY(cont[0][0], cont[0][1], texR)
      ctx.moveTo(first[0], first[1])
      for (let i = 1; i < cont.length; i++) {
        const xy = latLonToXY(cont[i][0], cont[i][1], texR)
        ctx.lineTo(xy[0], xy[1])
      }
      ctx.closePath()
      ctx.fill()
      ctx.stroke()
    })

    // City dots
    ctx.fillStyle = '#5eead4'
    CITIES.forEach(city => {
      const xy = latLonToXY(city[0], city[1], texR)
      ctx.beginPath()
      ctx.arc(xy[0], xy[1], 2.2, 0, Math.PI * 2)
      ctx.fill()
    })

    // Latitude/longitude grid
    ctx.strokeStyle = 'rgba(94, 234, 212, 0.2)'
    ctx.lineWidth = 0.5
    for (let lat = -80; lat <= 80; lat += 20) {
      ctx.beginPath()
      const start = latLonToXY(lat, 0, texR)
      ctx.moveTo(start[0], start[1])
      for (let lon = 5; lon <= 360; lon += 5) {
        const xy = latLonToXY(lat, lon, texR)
        ctx.lineTo(xy[0], xy[1])
      }
      ctx.stroke()
    }
    for (let lon = 0; lon < 360; lon += 30) {
      ctx.beginPath()
      const start = latLonToXY(-85, lon, texR)
      ctx.moveTo(start[0], start[1])
      for (let lat = -80; lat <= 80; lat += 5) {
        const xy = latLonToXY(lat, lon, texR)
        ctx.lineTo(xy[0], xy[1])
      }
      ctx.stroke()
    }

    const texture = new THREE.CanvasTexture(canvas)
    texture.wrapS = THREE.RepeatWrapping
    texture.wrapT = THREE.RepeatWrapping
    texture.anisotropy = 16
    return texture
  }, [])

  // Load portfolio textures with error handling
  const [portfolioTextures, setPortfolioTextures] = useState(
    PORTFOLIO.map(() => null)
  )
  useEffect(() => {
    const loader = new THREE.TextureLoader()
    let cancelled = false
    const texs = []
    PORTFOLIO.forEach((p, i) => {
      loader.load(
        p.image,
        (t) => {
          t.minFilter = THREE.LinearMipmapLinearFilter
          t.magFilter = THREE.LinearFilter
          t.generateMipmaps = true
          texs[i] = t
          if (!cancelled) setPortfolioTextures([...texs])
        },
        undefined,
        (err) => {
          console.warn(`Failed to load texture for ${p.name}:`, err)
          if (!cancelled) {
            texs[i] = null
            setPortfolioTextures([...texs])
          }
        }
      )
    })
    return () => { cancelled = true }
  }, [])

  // Fallback color texture for failed loads
  const fallbackTexture = useMemo(() => {
    const canvas = document.createElement('canvas')
    canvas.width = 8
    canvas.height = 8
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = '#222'
    ctx.fillRect(0, 0, 8, 8)
    const tex = new THREE.CanvasTexture(canvas)
    tex.minFilter = THREE.LinearFilter
    return tex
  }, [])

  // Starfield geometry
  const starGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry()
    const starCount = 2000
    const positions = new Float32Array(starCount * 3)
    const colors = new Float32Array(starCount * 3)

    for (let i = 0; i < starCount; i++) {
      const phi = Math.random() * Math.PI * 2
      const costheta = Math.random() * 2 - 1
      const theta = Math.acos(costheta)
      const r = 400 + Math.random() * 600
      positions[i * 3] = r * Math.sin(theta) * Math.cos(phi)
      positions[i * 3 + 1] = r * Math.sin(theta) * Math.sin(phi)
      positions[i * 3 + 2] = r * Math.cos(theta)
      const c = 0.5 + Math.random() * 0.5
      colors[i * 3] = c
      colors[i * 3 + 1] = c
      colors[i * 3 + 2] = c + 0.2
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
    return geometry
  }, [])

  const starMaterial = useMemo(() => new THREE.PointsMaterial({
    size: 0.8,
    vertexColors: true,
    transparent: true,
    opacity: 0.8
  }), [])

  // Mouse parallax
  const mousePos = useRef({ x: 0, y: 0 })
  useEffect(() => {
    const handleMouseMove = e => {
      const rect = e.currentTarget.getBoundingClientRect()
      const x = ((e.clientX - rect.left) / rect.width) - 0.5
      const y = ((e.clientY - rect.top) / rect.height) - 0.5
      mousePos.current = { x: x * 0.4, y: y * 0.4 }
    }
    document.addEventListener('mousemove', handleMouseMove)
    return () => document.removeEventListener('mousemove', handleMouseMove)
  }, [])

  // Animation loop
  useFrame(({ clock }) => {
    const t = clock.elapsedTime

    if (globeRef.current) {
      globeRef.current.rotation.y = t * 0.08 + mousePos.current.x * 0.3
      globeRef.current.rotation.x = mousePos.current.y * 0.15
    }
    if (atmosphereRef.current) {
      atmosphereRef.current.rotation.copy(globeRef.current.rotation)
    }
    if (wireframeRef.current) {
      wireframeRef.current.rotation.y = globeRef.current.rotation.y * 0.5
      wireframeRef.current.rotation.x = globeRef.current.rotation.x * 0.5
    }
    if (cityGroupRef.current) {
      cityGroupRef.current.rotation.y = globeRef.current.rotation.y
      cityGroupRef.current.rotation.x = globeRef.current.rotation.x
    }
    if (starsRef.current) {
      starsRef.current.rotation.y = t * 0.02
      starsRef.current.rotation.x = t * 0.01
    }

    // Animate orbit planes
    if (orbitGroupRef.current) {
      orbitGroupRef.current.children.forEach((mesh, i) => {
        if (mesh.userData) {
          const a = mesh.userData.angle + t * 0.3
          const radius = mesh.userData.radius
          mesh.position.x = Math.sin(a) * radius
          mesh.position.z = Math.cos(a) * radius
          mesh.position.y = mesh.userData.baseY + Math.sin(t * 1.2 + i) * 0.05
        }
      })
    }
  })

  const globeRadius = 1.8

  return (
    <>
      {/* Starfield */}
      <points ref={starsRef} geometry={starGeometry} material={starMaterial} />

      {/* Globe */}
      <mesh ref={globeRef}>
        <icosahedronGeometry args={[globeRadius, 4]} />
        <meshStandardMaterial
          map={globeTexture}
          emissive={new THREE.Color(0x0a2040)}
          emissiveIntensity={0.2}
          metalness={0}
          roughness={0.7}
        />
      </mesh>

      {/* Atmosphere */}
      <mesh ref={atmosphereRef}>
        <sphereGeometry args={[globeRadius * 1.02, 64, 64]} />
        <atmosphereMaterial
          side={THREE.BackSide}
          transparent
          blending={THREE.AdditiveBlending}
        />
      </mesh>

      {/* Wireframe */}
      <lineSegments ref={wireframeRef}>
        <edgesGeometry args={[new THREE.IcosahedronGeometry(globeRadius * 1.005, 3)]} />
        <lineBasicMaterial color={0x5eead4} transparent opacity={0.1} />
      </lineSegments>

      {/* City lights */}
      <group ref={cityGroupRef}>
        {CITIES.map((city, i) => {
          const phi = city[0] * Math.PI / 180
          const lam = city[1] * Math.PI / 180
          const x = globeRadius * Math.cos(phi) * Math.cos(lam)
          const y = globeRadius * Math.sin(phi)
          const z = globeRadius * Math.cos(phi) * Math.sin(lam)
          return (
            <pointLight
              key={i}
              position={[x, y, z]}
              color={0x5eead4}
              intensity={0.8}
              distance={3}
              decay={2}
            />
          )
        })}
      </group>

      {/* Orbiting portfolio planes */}
      <group ref={orbitGroupRef}>
        {PORTFOLIO.map((item, i) => {
          const angle = (i / PORTFOLIO.length) * Math.PI * 2
          const radius = globeRadius * 2.8
          const x = Math.sin(angle) * radius
          const z = Math.cos(angle) * radius
          const y = (Math.random() - 0.5) * 0.3

          return (
            <mesh
              key={item.name}
              userData={{
                angle: angle,
                radius: radius,
                baseY: y
              }}
            >
              <planeGeometry args={[1.4, 0.88]} />
              <meshBasicMaterial
                map={portfolioTextures[i] || fallbackTexture}
                transparent
                opacity={0.95}
                toneMapped={false}
              />
            </mesh>
          )
        })}
      </group>

      {/* Lights */}
      <ambientLight intensity={1.5} color={0x404060} />
      <directionalLight position={[5, 3, 5]} intensity={0.8} color={0x5eead4} />
    </>
  )
}
