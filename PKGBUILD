pkgname=catos-niri-noctaliav5
pkgver=1.0.0
pkgrel=1
pkgdesc="CachyOS Niri + Noctalia v5 "
install=catos-niri-noctaliav5.install
arch=('any')
url="https://github.com/YeFaDa/${pkgname}"
license=('GPL3')

depends=(
    'niri'
    'noctalia-git'
    'noctalia-greeter-git'
    'dconf'
    'adw-gtk-theme'
    'qt6ct'
    'polkit-gnome'
    'nwg-look'
)

makedepends=('git')

source=("git+https://github.com/YeFaDa/catos-niri-noctaliav5.git")
sha256sums=('SKIP')

package() {
    install -d "${pkgdir}/etc"
    cp -rf "${srcdir}/${pkgname}/etc" "${pkgdir}/"
    chmod -R 755 "${pkgdir}/etc/skel"
    install -d "${pkgdir}/usr/share/${pkgname}"
    cp -f "${srcdir}/${pkgname}/usr/share/${pkgname}/greetd-config.toml" "${pkgdir}/usr/share/${pkgname}/"

}
