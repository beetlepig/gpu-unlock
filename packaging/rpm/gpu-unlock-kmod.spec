# akmod/kmod flavor for rpm-ostree hosts (Fedora Silverblue/Kinoite) and any
# other installs where DKMS cannot build or sign a module for the live root.
# kmodtool and akmods build and sign gpu_unlock for every installed kernel
# instead; see README.md's "Secure Boot and rpm-ostree" section for setup.
%global debug_package %{nil}

Name:           gpu-unlock-kmod
Version:        2.0.0
Release:        1%{?dist}
Summary:        Kernel module (kmod) for gpu-unlock
License:        GPL-2.0-only
URL:            https://github.com/Zagitta/gpu-unlock

Source0:        gpu-unlock-%{version}.tar.xz

BuildRequires:  gcc
BuildRequires:  elfutils-libelf-devel
BuildRequires:  kmodtool

# Pulls in gpu-unlock-firmware for both the firmware blobs and the
# "-common" Provides kmodtool's akmod package always requires.
%global AkmodsBuildRequires gpu-unlock-firmware = %{version}

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --kmodname gpu-unlock --akmod %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null)}

%description
RTX 3090 BF16 unlock kernel module, loaded ahead of nvidia on every boot. It
does nothing unless gpu_unlock.targets= is on the kernel command line.

This is the akmod/kmod build: akmods builds and signs it for every
installed kernel instead of DKMS, for rpm-ostree hosts such as Fedora
Silverblue/Kinoite where DKMS cannot build on the live root.

%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool --target %{_target_cpu} --kmodname gpu-unlock --akmod %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c
test "$(cat gpu-unlock-%{version}/VERSION)" = "%{version}"

for kernel_version in %{?kernel_versions}; do
    cp -a gpu-unlock-%{version}/kernel/gpu_unlock _kmod_build_${kernel_version%%___*}
done

%build
for kernel_version in %{?kernel_versions}; do
    make V=1 %{?_smp_mflags} -C ${kernel_version##*___} M=${PWD}/_kmod_build_${kernel_version%%___*} modules
done

%install
for kernel_version in %{?kernel_versions}; do
    mkdir -p %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
    install -D -m 755 _kmod_build_${kernel_version%%___*}/gpu_unlock.ko \
        %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
done
%{?akmod_install}

%changelog
* Tue Oct 27 2026 Zagitta <zetlon+github@gmail.com> - 2.0.0-1
- Add Turing and Ada Lovelace support.

* Mon Sep 28 2026 Zagitta <zetlon+github@gmail.com> - 1.0.0-1
- Initial release.
