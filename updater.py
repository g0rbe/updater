#!/bin/python

import subprocess
import os
import sys

class CustomError(BaseException):
	def __init__(self, message):
		self.message = message

class PackageManager:
		
	# Get the system's package manager
	# Currently supported: apt / dnf
	def __init__(self):
		
		if os.access("/usr/bin/apt", os.X_OK):
			self.package_manager = "apt"
		elif os.access("/usr/bin/dnf", os.X_OK):
			self.package_manager = "dnf"
		else:
			raise CustomError("No usable package manager found!")

	# Update package informations with apt
	def __update_apt(self):
		
		command = ["/usr/bin/apt", "update"]
		
		try:
			subprocess.run(command, capture_output=True, check=True, text=True)
		except subprocess.CalledProcessError as proc_err:
			raise CustomError(f"Failed update with apt:\n{procerr.stderr}\n")
		except Exception as e:
			raise CustomError(f"Unknow error while updating with apt: {e}") 
	
	# Update package informations with dnf 
	def __update_dnf(self):
		
		command = ["/usr/bin/dnf", "check-update"]
		
		try:
			subprocess.run(command, capture_output=True, check=True, text=True)
		except subprocess.CalledProcessError as proc_err:
			if proc_err.returncode != 100:
				raise CustomError(f"Failed update with dnf:\n{proc_err.stderr}\n")
		except Exception as e:
			raise CustomError(f"Unknow error while updating with dnf: {e}") 
	
	# Update
	def update(self):
		
		if self.package_manager == "apt":
			self.__update_apt()
		elif self.package_manager == "dnf":
			self.__update_dnf()
	
	# Return a list of packages that needs to upgrade (apt)	
	def __list_upgradable_apt(self):
		
		command = ["/usr/bin/apt", "list", "--upgradable"]
		
		try:
			output = subprocess.run(command, capture_output=True, check=True, text=True)
		except subprocess.CalledProcessError as proc_err:
			raise CustomError(f"Failed to list upgradable with apt:\n{procerr.stderr}\n")
		except Exception as e:
			raise CustomError(f"Unknow error while listing upgradable with apt: {e}")
		else:
			packages = []
			
			for line in output.stdout.splitlines():
				if "[upgradable from" in line:
					packages.append(line.split("/")[0])
			
			return packages
	
	# Return a list of packages that needs to upgrade (dnf)	
	def __list_upgradable_dnf(self):
		
		command = ["/usr/bin/dnf", "list", "--updates"]
		
		try:
			output = subprocess.run(command, capture_output=True, check=True, text=True)
		except subprocess.CalledProcessError as proc_err:
			raise CustomError(f"Failed list upgradable with dnf:\n{procerr.stderr}\n")
		except Exception as e:
			raise CustomError(f"Unknow error while listing upgradable with dnf: {e}")
		else:
			
			packages = []
			
			for line in output.stdout.splitlines():
				if "updates" in line:
					packages.append(line.split(" ")[0].split(".")[0])
			
			return packages

	# Return a list of packages that needs to upgrade
	def list_upgradable(self):
		
		if self.package_manager == "apt":
			return self.__list_upgradable_apt()
		elif self.package_manager == "dnf":
			return self.__list_upgradable_dnf()

	def __upgrade_apt(self):
		
		command = ["/usr/bin/apt", "dist-upgrade", "-y"]
		
		try:
			output = subprocess.run(command, capture_output=True, check=True, text=True)
		except subprocess.CalledProcessError as proc_err:
			raise CustomError(f"Failed upgrade with apt:\n{procerr.stderr}\n")
		except Exception as e:
			raise CustomError(f"Unknow error while upgrading with apt: {e}")
			
	def __upgrade_dnf(self):
		
		command = ["/usr/bin/dnf", "upgrade", "-y"]
		
		try:
			output = subprocess.run(command, capture_output=True, check=True, text=True)
		except subprocess.CalledProcessError as proc_err:
			raise CustomError(f"Failed upgrade with dnf:\n{procerr.stderr}\n")
		except Exception as e:
			raise CustomError(f"Unknow error while upgrading with dnf: {e}")
		
	def upgrade(self):
		
		if self.package_manager == "apt":
			self.__upgrade_apt()
		elif self.package_manager == "dnf":
			self.__upgrade_dnf();	
	

if __name__ == "__main__":
	
	if os.geteuid() != 0:
		print("Run as root!", file=sys.stderr)
		sys.exit(1)
	

	try:

		pm = PackageManager()
		
		print("Updating local chache...")
		pm.update()
		
		print("Getting the list of upgradable packages...")
		packages = pm.list_upgradable()
		
		if len(packages) == 0:
			print("Nothing to update!")
			sys.exit(0)
		else:
			print(f"Upgrading packages: {packages}") 
		
		print("Upgrading...")
		pm.upgrade() 
		
		
	except CustomError as e:
		print(e.message, file=sys.stderr)
			
			 
