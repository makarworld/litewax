
import eospy.cleos
import eospy.keys
import pytz
import datetime as dt

class atomicdropsx:
    def __init__(self, username: str, permission: str="active", node: str="https://wax.greymass.com"):
        self.wax = eospy.cleos.Cleos(url=node, version='v1')
        self.username = username
        self.permission = permission

    def generatePayload(self, account: str, name: str) -> dict:
        return {
            "account": account,
            "name": name,
            "authorization": [{
                "actor": self.username,
                "permission": self.permission,
            }],
        }

    def return_payload(self, payload, args):
        data = self.wax.abi_json_to_bin(
            payload['account'], 
            payload['name'], 
            args
        )
        payload['data'] = data['binargs']
        return payload

    # ACTIONS
    def accstats_s(self, drop_id: int, counter: int, last_claim_time: int, used_nonces: list):
        """
        ## ACTION: atomicdropsx.accstats_s
        - Parametrs:
        methods:
            - drop_id: uint64
            - counter: uint64
            - last_claim_time: uint32
            - used_nonces: uint64[]
        """

        accstats_s_args = {
            "drop_id": drop_id,
            "counter": counter,
            "last_claim_time": last_claim_time,
            "used_nonces": used_nonces
        }
        accstats_s_base = self.generatePayload("atomicdropsx", "accstats_s")
        return accstats_s_args, accstats_s_base


    def addcolbal(self, owner: str, collection_name: str, token_to_transfer: str):
        """
        ## ACTION: atomicdropsx.addcolbal
        - Parametrs:
        methods:
            - owner: name
            - collection_name: name
            - token_to_transfer: asset
        """

        addcolbal_args = {
            "owner": owner,
            "collection_name": collection_name,
            "token_to_transfer": token_to_transfer
        }
        addcolbal_base = self.generatePayload("atomicdropsx", "addcolbal")
        return addcolbal_args, addcolbal_base


    def addconftoken(self, token_contract: str, token_symbol: str):
        """
        ## ACTION: atomicdropsx.addconftoken
        - Parametrs:
        methods:
            - token_contract: name
            - token_symbol: symbol
        """

        addconftoken_args = {
            "token_contract": token_contract,
            "token_symbol": token_symbol
        }
        addconftoken_base = self.generatePayload("atomicdropsx", "addconftoken")
        return addconftoken_args, addconftoken_base


    def adddelphi(self, delphi_pair_name: str, invert_delphi_pair: bool, listing_symbol: str, settlement_symbol: str):
        """
        ## ACTION: atomicdropsx.adddelphi
        - Parametrs:
        methods:
            - delphi_pair_name: name
            - invert_delphi_pair: bool
            - listing_symbol: symbol
            - settlement_symbol: symbol
        """

        adddelphi_args = {
            "delphi_pair_name": delphi_pair_name,
            "invert_delphi_pair": invert_delphi_pair,
            "listing_symbol": listing_symbol,
            "settlement_symbol": settlement_symbol
        }
        adddelphi_base = self.generatePayload("atomicdropsx", "adddelphi")
        return adddelphi_args, adddelphi_base


    def addtowl(self, authorized_account: str, drop_id: int, accounts_to_add: list):
        """
        ## ACTION: atomicdropsx.addtowl
        - Parametrs:
        methods:
            - authorized_account: name
            - drop_id: uint64
            - accounts_to_add: name[]
        """

        addtowl_args = {
            "authorized_account": authorized_account,
            "drop_id": drop_id,
            "accounts_to_add": accounts_to_add
        }
        addtowl_base = self.generatePayload("atomicdropsx", "addtowl")
        return addtowl_args, addtowl_base


    def assertdrop(self, drop_id: int, assets_to_mint_to_assert: list, listing_price_to_assert: str, settlement_symbol_to_assert: str):
        """
        ## ACTION: atomicdropsx.assertdrop
        - Parametrs:
        methods:
            - drop_id: uint64
            - assets_to_mint_to_assert: ASSET_TO_MINT[]
            - listing_price_to_assert: asset
            - settlement_symbol_to_assert: symbol
        """

        assertdrop_args = {
            "drop_id": drop_id,
            "assets_to_mint_to_assert": assets_to_mint_to_assert,
            "listing_price_to_assert": listing_price_to_assert,
            "settlement_symbol_to_assert": settlement_symbol_to_assert
        }
        assertdrop_base = self.generatePayload("atomicdropsx", "assertdrop")
        return assertdrop_args, assertdrop_base


    def authkeys_s(self, key: str, key_limit: int, key_limit_cooldown: int, counter: int, last_claim_time: int):
        """
        ## ACTION: atomicdropsx.authkeys_s
        - Parametrs:
        methods:
            - key: public_key
            - key_limit: uint64
            - key_limit_cooldown: uint32
            - counter: uint64
            - last_claim_time: uint32
        """

        authkeys_s_args = {
            "key": key,
            "key_limit": key_limit,
            "key_limit_cooldown": key_limit_cooldown,
            "counter": counter,
            "last_claim_time": last_claim_time
        }
        authkeys_s_base = self.generatePayload("atomicdropsx", "authkeys_s")
        return authkeys_s_args, authkeys_s_base


    def balances_s(self, identifier: str, quantities: list):
        """
        ## ACTION: atomicdropsx.balances_s
        - Parametrs:
        methods:
            - identifier: name
            - quantities: asset[]
        """

        balances_s_args = {
            "identifier": identifier,
            "quantities": quantities
        }
        balances_s_base = self.generatePayload("atomicdropsx", "balances_s")
        return balances_s_args, balances_s_base


    def buyramproxy(self, collection_to_credit: str, quantity: str):
        """
        ## ACTION: atomicdropsx.buyramproxy
        - Parametrs:
        methods:
            - collection_to_credit: name
            - quantity: asset
        """

        buyramproxy_args = {
            "collection_to_credit": collection_to_credit,
            "quantity": quantity
        }
        buyramproxy_base = self.generatePayload("atomicdropsx", "buyramproxy")
        return buyramproxy_args, buyramproxy_base


    def claimdrop(self, claimer: str, drop_id: int, claim_amount: int, intended_delphi_median: int, referrer: str, country: str):
        """
        ## ACTION: atomicdropsx.claimdrop
        - Parametrs:
        methods:
            - claimer: name
            - drop_id: uint64
            - claim_amount: uint64
            - intended_delphi_median: uint64
            - referrer: string
            - country: string
        """

        claimdrop_args = {
            "claimer": claimer,
            "drop_id": drop_id,
            "claim_amount": claim_amount,
            "intended_delphi_median": intended_delphi_median,
            "referrer": referrer,
            "country": country
        }
        claimdrop_base = self.generatePayload("atomicdropsx", "claimdrop")
        return claimdrop_args, claimdrop_base


    def claimdropkey(self, claimer: str, drop_id: int, claim_amount: int, intended_delphi_median: int, authkey_key: str, signature_nonce: int, claim_signature: str, referrer: str, country: str):
        """
        ## ACTION: atomicdropsx.claimdropkey
        - Parametrs:
        methods:
            - claimer: name
            - drop_id: uint64
            - claim_amount: uint64
            - intended_delphi_median: uint64
            - authkey_key: public_key
            - signature_nonce: uint64
            - claim_signature: signature
            - referrer: string
            - country: string
        """

        claimdropkey_args = {
            "claimer": claimer,
            "drop_id": drop_id,
            "claim_amount": claim_amount,
            "intended_delphi_median": intended_delphi_median,
            "authkey_key": authkey_key,
            "signature_nonce": signature_nonce,
            "claim_signature": claim_signature,
            "referrer": referrer,
            "country": country
        }
        claimdropkey_base = self.generatePayload("atomicdropsx", "claimdropkey")
        return claimdropkey_args, claimdropkey_base


    def claimdropwl(self, claimer: str, drop_id: int, claim_amount: int, intended_delphi_median: int, referrer: str, country: str):
        """
        ## ACTION: atomicdropsx.claimdropwl
        - Parametrs:
        methods:
            - claimer: name
            - drop_id: uint64
            - claim_amount: uint64
            - intended_delphi_median: uint64
            - referrer: string
            - country: string
        """

        claimdropwl_args = {
            "claimer": claimer,
            "drop_id": drop_id,
            "claim_amount": claim_amount,
            "intended_delphi_median": intended_delphi_median,
            "referrer": referrer,
            "country": country
        }
        claimdropwl_base = self.generatePayload("atomicdropsx", "claimdropwl")
        return claimdropwl_args, claimdropwl_base


    def clearkeys(self, drop_id: int, max_keys_to_clear: int):
        """
        ## ACTION: atomicdropsx.clearkeys
        - Parametrs:
        methods:
            - drop_id: uint64
            - max_keys_to_clear: uint64
        """

        clearkeys_args = {
            "drop_id": drop_id,
            "max_keys_to_clear": max_keys_to_clear
        }
        clearkeys_base = self.generatePayload("atomicdropsx", "clearkeys")
        return clearkeys_args, clearkeys_base


    def clearwl(self, drop_id: int, max_accounts_to_clear: int):
        """
        ## ACTION: atomicdropsx.clearwl
        - Parametrs:
        methods:
            - drop_id: uint64
            - max_accounts_to_clear: uint64
        """

        clearwl_args = {
            "drop_id": drop_id,
            "max_accounts_to_clear": max_accounts_to_clear
        }
        clearwl_base = self.generatePayload("atomicdropsx", "clearwl")
        return clearwl_args, clearwl_base


    def config_s(self, version: str, drop_counter: int, authkey_counter: int, supported_tokens: list, supported_symbol_pairs: list, atomicassets_account: str, delphioracle_account: str):
        """
        ## ACTION: atomicdropsx.config_s
        - Parametrs:
        methods:
            - version: string
            - drop_counter: uint64
            - authkey_counter: uint64
            - supported_tokens: extended_symbol[]
            - supported_symbol_pairs: SYMBOLPAIR[]
            - atomicassets_account: name
            - delphioracle_account: name
        """

        config_s_args = {
            "version": version,
            "drop_counter": drop_counter,
            "authkey_counter": authkey_counter,
            "supported_tokens": supported_tokens,
            "supported_symbol_pairs": supported_symbol_pairs,
            "atomicassets_account": atomicassets_account,
            "delphioracle_account": delphioracle_account
        }
        config_s_base = self.generatePayload("atomicdropsx", "config_s")
        return config_s_args, config_s_base


    def countrylists_s(self, drop_id: int, allowed_countries: list):
        """
        ## ACTION: atomicdropsx.countrylists_s
        - Parametrs:
        methods:
            - drop_id: uint64
            - allowed_countries: string[]
        """

        countrylists_s_args = {
            "drop_id": drop_id,
            "allowed_countries": allowed_countries
        }
        countrylists_s_base = self.generatePayload("atomicdropsx", "countrylists_s")
        return countrylists_s_args, countrylists_s_base


    def createdrop(self, authorized_account: str, collection_name: str, assets_to_mint: list, listing_price: str, settlement_symbol: str, price_recipient: str, auth_required: bool, max_claimable: int, account_limit: int, account_limit_cooldown: int, start_time: int, end_time: int, display_data: str):
        """
        ## ACTION: atomicdropsx.createdrop
        - Parametrs:
        methods:
            - authorized_account: name
            - collection_name: name
            - assets_to_mint: ASSET_TO_MINT[]
            - listing_price: asset
            - settlement_symbol: symbol
            - price_recipient: name
            - auth_required: bool
            - max_claimable: uint64
            - account_limit: uint64
            - account_limit_cooldown: uint32
            - start_time: uint32
            - end_time: uint32
            - display_data: string
        """

        createdrop_args = {
            "authorized_account": authorized_account,
            "collection_name": collection_name,
            "assets_to_mint": assets_to_mint,
            "listing_price": listing_price,
            "settlement_symbol": settlement_symbol,
            "price_recipient": price_recipient,
            "auth_required": auth_required,
            "max_claimable": max_claimable,
            "account_limit": account_limit,
            "account_limit_cooldown": account_limit_cooldown,
            "start_time": start_time,
            "end_time": end_time,
            "display_data": display_data
        }
        createdrop_base = self.generatePayload("atomicdropsx", "createdrop")
        return createdrop_args, createdrop_base


    def createkey(self, authorized_account: str, drop_id: int, key: str, key_limit: int, key_limit_cooldown: int):
        """
        ## ACTION: atomicdropsx.createkey
        - Parametrs:
        methods:
            - authorized_account: name
            - drop_id: uint64
            - key: public_key
            - key_limit: uint64
            - key_limit_cooldown: uint32
        """

        createkey_args = {
            "authorized_account": authorized_account,
            "drop_id": drop_id,
            "key": key,
            "key_limit": key_limit,
            "key_limit_cooldown": key_limit_cooldown
        }
        createkey_base = self.generatePayload("atomicdropsx", "createkey")
        return createkey_args, createkey_base


    def drops_s(self, drop_id: int, collection_name: str, assets_to_mint: list, listing_price: str, settlement_symbol: str, price_recipient: str, fee_rate: float, auth_required: bool, account_limit: int, account_limit_cooldown: int, max_claimable: int, current_claimed: int, start_time: int, end_time: int, display_data: str):
        """
        ## ACTION: atomicdropsx.drops_s
        - Parametrs:
        methods:
            - drop_id: uint64
            - collection_name: name
            - assets_to_mint: ASSET_TO_MINT[]
            - listing_price: asset
            - settlement_symbol: symbol
            - price_recipient: name
            - fee_rate: float64
            - auth_required: bool
            - account_limit: uint64
            - account_limit_cooldown: uint32
            - max_claimable: uint64
            - current_claimed: uint64
            - start_time: uint32
            - end_time: uint32
            - display_data: string
        """

        drops_s_args = {
            "drop_id": drop_id,
            "collection_name": collection_name,
            "assets_to_mint": assets_to_mint,
            "listing_price": listing_price,
            "settlement_symbol": settlement_symbol,
            "price_recipient": price_recipient,
            "fee_rate": fee_rate,
            "auth_required": auth_required,
            "account_limit": account_limit,
            "account_limit_cooldown": account_limit_cooldown,
            "max_claimable": max_claimable,
            "current_claimed": current_claimed,
            "start_time": start_time,
            "end_time": end_time,
            "display_data": display_data
        }
        drops_s_base = self.generatePayload("atomicdropsx", "drops_s")
        return drops_s_args, drops_s_base


    def eraseaccstat(self, account: str, drop_id: int):
        """
        ## ACTION: atomicdropsx.eraseaccstat
        - Parametrs:
        methods:
            - account: name
            - drop_id: uint64
        """

        eraseaccstat_args = {
            "account": account,
            "drop_id": drop_id
        }
        eraseaccstat_base = self.generatePayload("atomicdropsx", "eraseaccstat")
        return eraseaccstat_args, eraseaccstat_base


    def erasedrop(self, authorized_account: str, drop_id: int):
        """
        ## ACTION: atomicdropsx.erasedrop
        - Parametrs:
        methods:
            - authorized_account: name
            - drop_id: uint64
        """

        erasedrop_args = {
            "authorized_account": authorized_account,
            "drop_id": drop_id
        }
        erasedrop_base = self.generatePayload("atomicdropsx", "erasedrop")
        return erasedrop_args, erasedrop_base


    def erasefromwl(self, authorized_account: str, drop_id: int, accounts_to_remove: list):
        """
        ## ACTION: atomicdropsx.erasefromwl
        - Parametrs:
        methods:
            - authorized_account: name
            - drop_id: uint64
            - accounts_to_remove: name[]
        """

        erasefromwl_args = {
            "authorized_account": authorized_account,
            "drop_id": drop_id,
            "accounts_to_remove": accounts_to_remove
        }
        erasefromwl_base = self.generatePayload("atomicdropsx", "erasefromwl")
        return erasefromwl_args, erasefromwl_base


    def erasekey(self, authorized_account: str, drop_id: int, key: str):
        """
        ## ACTION: atomicdropsx.erasekey
        - Parametrs:
        methods:
            - authorized_account: name
            - drop_id: uint64
            - key: public_key
        """

        erasekey_args = {
            "authorized_account": authorized_account,
            "drop_id": drop_id,
            "key": key
        }
        erasekey_base = self.generatePayload("atomicdropsx", "erasekey")
        return erasekey_args, erasekey_base


    def extended_symbol(self, sym: str, contract: str):
        """
        ## ACTION: atomicdropsx.extended_symbol
        - Parametrs:
        methods:
            - sym: symbol
            - contract: name
        """

        extended_symbol_args = {
            "sym": sym,
            "contract": contract
        }
        extended_symbol_base = self.generatePayload("atomicdropsx", "extended_symbol")
        return extended_symbol_args, extended_symbol_base


    def init(self, ):
        """
        ## ACTION: atomicdropsx.init
        - Parametrs:
        methods:
            
        """

        init_args = {

        }
        init_base = self.generatePayload("atomicdropsx", "init")
        return init_args, init_base


    def lognewdrop(self, drop_id: int, collection_name: str, assets_to_mint: list, listing_price: str, settlement_symbol: str, price_recipient: str, auth_required: bool, max_claimable: int, account_limit: int, account_limit_cooldown: int, start_time: int, end_time: int, display_data: str):
        """
        ## ACTION: atomicdropsx.lognewdrop
        - Parametrs:
        methods:
            - drop_id: uint64
            - collection_name: name
            - assets_to_mint: ASSET_TO_MINT[]
            - listing_price: asset
            - settlement_symbol: symbol
            - price_recipient: name
            - auth_required: bool
            - max_claimable: uint64
            - account_limit: uint64
            - account_limit_cooldown: uint32
            - start_time: uint32
            - end_time: uint32
            - display_data: string
        """

        lognewdrop_args = {
            "drop_id": drop_id,
            "collection_name": collection_name,
            "assets_to_mint": assets_to_mint,
            "listing_price": listing_price,
            "settlement_symbol": settlement_symbol,
            "price_recipient": price_recipient,
            "auth_required": auth_required,
            "max_claimable": max_claimable,
            "account_limit": account_limit,
            "account_limit_cooldown": account_limit_cooldown,
            "start_time": start_time,
            "end_time": end_time,
            "display_data": display_data
        }
        lognewdrop_base = self.generatePayload("atomicdropsx", "lognewdrop")
        return lognewdrop_args, lognewdrop_base


    def rambalances_s(self, collection_name: str, byte_balance: int):
        """
        ## ACTION: atomicdropsx.rambalances_s
        - Parametrs:
        methods:
            - collection_name: name
            - byte_balance: int64
        """

        rambalances_s_args = {
            "collection_name": collection_name,
            "byte_balance": byte_balance
        }
        rambalances_s_base = self.generatePayload("atomicdropsx", "rambalances_s")
        return rambalances_s_args, rambalances_s_base


    def ramrefunds_s(self, refund_type: str, to_block: int):
        """
        ## ACTION: atomicdropsx.ramrefunds_s
        - Parametrs:
        methods:
            - refund_type: name
            - to_block: int64
        """

        ramrefunds_s_args = {
            "refund_type": refund_type,
            "to_block": to_block
        }
        ramrefunds_s_base = self.generatePayload("atomicdropsx", "ramrefunds_s")
        return ramrefunds_s_args, ramrefunds_s_base


    def refundram(self, refund_type: str, from_block: int, to_block: int, ram_refund_data: list):
        """
        ## ACTION: atomicdropsx.refundram
        - Parametrs:
        methods:
            - refund_type: name
            - from_block: uint64
            - to_block: uint64
            - ram_refund_data: RAM_REFUND_DATA[]
        """

        refundram_args = {
            "refund_type": refund_type,
            "from_block": from_block,
            "to_block": to_block,
            "ram_refund_data": ram_refund_data
        }
        refundram_base = self.generatePayload("atomicdropsx", "refundram")
        return refundram_args, refundram_base


    def remcolbal(self, authorized_account: str, collection_name: str, recipient: str, token_to_transfer: str):
        """
        ## ACTION: atomicdropsx.remcolbal
        - Parametrs:
        methods:
            - authorized_account: name
            - collection_name: name
            - recipient: name
            - token_to_transfer: asset
        """

        remcolbal_args = {
            "authorized_account": authorized_account,
            "collection_name": collection_name,
            "recipient": recipient,
            "token_to_transfer": token_to_transfer
        }
        remcolbal_base = self.generatePayload("atomicdropsx", "remcolbal")
        return remcolbal_args, remcolbal_base


    def setcountries(self, authorized_account: str, drop_id: int, allowed_countries: list):
        """
        ## ACTION: atomicdropsx.setcountries
        - Parametrs:
        methods:
            - authorized_account: name
            - drop_id: uint64
            - allowed_countries: string[]
        """

        setcountries_args = {
            "authorized_account": authorized_account,
            "drop_id": drop_id,
            "allowed_countries": allowed_countries
        }
        setcountries_base = self.generatePayload("atomicdropsx", "setcountries")
        return setcountries_args, setcountries_base


    def setdropauth(self, authorized_account: str, drop_id: int, auth_required: bool):
        """
        ## ACTION: atomicdropsx.setdropauth
        - Parametrs:
        methods:
            - authorized_account: name
            - drop_id: uint64
            - auth_required: bool
        """

        setdropauth_args = {
            "authorized_account": authorized_account,
            "drop_id": drop_id,
            "auth_required": auth_required
        }
        setdropauth_base = self.generatePayload("atomicdropsx", "setdropauth")
        return setdropauth_args, setdropauth_base


    def setdropdata(self, authorized_account: str, drop_id: int, display_data: str):
        """
        ## ACTION: atomicdropsx.setdropdata
        - Parametrs:
        methods:
            - authorized_account: name
            - drop_id: uint64
            - display_data: string
        """

        setdropdata_args = {
            "authorized_account": authorized_account,
            "drop_id": drop_id,
            "display_data": display_data
        }
        setdropdata_base = self.generatePayload("atomicdropsx", "setdropdata")
        return setdropdata_args, setdropdata_base


    def setdroplimit(self, authorized_account: str, drop_id: int, account_limit: int, account_limit_cooldown: int):
        """
        ## ACTION: atomicdropsx.setdroplimit
        - Parametrs:
        methods:
            - authorized_account: name
            - drop_id: uint64
            - account_limit: uint64
            - account_limit_cooldown: uint32
        """

        setdroplimit_args = {
            "authorized_account": authorized_account,
            "drop_id": drop_id,
            "account_limit": account_limit,
            "account_limit_cooldown": account_limit_cooldown
        }
        setdroplimit_base = self.generatePayload("atomicdropsx", "setdroplimit")
        return setdroplimit_args, setdroplimit_base


    def setdropmax(self, authorized_account: str, drop_id: int, new_max_claimable: int):
        """
        ## ACTION: atomicdropsx.setdropmax
        - Parametrs:
        methods:
            - authorized_account: name
            - drop_id: uint64
            - new_max_claimable: uint64
        """

        setdropmax_args = {
            "authorized_account": authorized_account,
            "drop_id": drop_id,
            "new_max_claimable": new_max_claimable
        }
        setdropmax_base = self.generatePayload("atomicdropsx", "setdropmax")
        return setdropmax_args, setdropmax_base


    def setdropprice(self, authorized_account: str, drop_id: int, listing_price: str, settlement_symbol: str):
        """
        ## ACTION: atomicdropsx.setdropprice
        - Parametrs:
        methods:
            - authorized_account: name
            - drop_id: uint64
            - listing_price: asset
            - settlement_symbol: symbol
        """

        setdropprice_args = {
            "authorized_account": authorized_account,
            "drop_id": drop_id,
            "listing_price": listing_price,
            "settlement_symbol": settlement_symbol
        }
        setdropprice_base = self.generatePayload("atomicdropsx", "setdropprice")
        return setdropprice_args, setdropprice_base


    def setdroptimes(self, authorized_account: str, drop_id: int, start_time: int, end_time: int):
        """
        ## ACTION: atomicdropsx.setdroptimes
        - Parametrs:
        methods:
            - authorized_account: name
            - drop_id: uint64
            - start_time: uint32
            - end_time: uint32
        """

        setdroptimes_args = {
            "authorized_account": authorized_account,
            "drop_id": drop_id,
            "start_time": start_time,
            "end_time": end_time
        }
        setdroptimes_base = self.generatePayload("atomicdropsx", "setdroptimes")
        return setdroptimes_args, setdroptimes_base


    def setfeerate(self, drop_id: int, fee_rate: float):
        """
        ## ACTION: atomicdropsx.setfeerate
        - Parametrs:
        methods:
            - drop_id: uint64
            - fee_rate: float64
        """

        setfeerate_args = {
            "drop_id": drop_id,
            "fee_rate": fee_rate
        }
        setfeerate_base = self.generatePayload("atomicdropsx", "setfeerate")
        return setfeerate_args, setfeerate_base


    def setversion(self, new_version: str):
        """
        ## ACTION: atomicdropsx.setversion
        - Parametrs:
        methods:
            - new_version: string
        """

        setversion_args = {
            "new_version": new_version
        }
        setversion_base = self.generatePayload("atomicdropsx", "setversion")
        return setversion_args, setversion_base


    def triggerdrop(self, authorized_account: str, drop_id: int, recipient: str, amount: int, trigger_provider: str, trigger_identifier: str):
        """
        ## ACTION: atomicdropsx.triggerdrop
        - Parametrs:
        methods:
            - authorized_account: name
            - drop_id: uint64
            - recipient: name
            - amount: uint64
            - trigger_provider: string
            - trigger_identifier: string
        """

        triggerdrop_args = {
            "authorized_account": authorized_account,
            "drop_id": drop_id,
            "recipient": recipient,
            "amount": amount,
            "trigger_provider": trigger_provider,
            "trigger_identifier": trigger_identifier
        }
        triggerdrop_base = self.generatePayload("atomicdropsx", "triggerdrop")
        return triggerdrop_args, triggerdrop_base


    def triggers_s(self, trigger_provider: str, trigger_identifier: str):
        """
        ## ACTION: atomicdropsx.triggers_s
        - Parametrs:
        methods:
            - trigger_provider: string
            - trigger_identifier: string
        """

        triggers_s_args = {
            "trigger_provider": trigger_provider,
            "trigger_identifier": trigger_identifier
        }
        triggers_s_base = self.generatePayload("atomicdropsx", "triggers_s")
        return triggers_s_args, triggers_s_base


    def whitelist_s(self, account: str):
        """
        ## ACTION: atomicdropsx.whitelist_s
        - Parametrs:
        methods:
            - account: name
        """

        whitelist_s_args = {
            "account": account
        }
        whitelist_s_base = self.generatePayload("atomicdropsx", "whitelist_s")
        return whitelist_s_args, whitelist_s_base


    def withdraw(self, owner: str, token_to_withdraw: str):
        """
        ## ACTION: atomicdropsx.withdraw
        - Parametrs:
        methods:
            - owner: name
            - token_to_withdraw: asset
        """

        withdraw_args = {
            "owner": owner,
            "token_to_withdraw": token_to_withdraw
        }
        withdraw_base = self.generatePayload("atomicdropsx", "withdraw")
        return withdraw_args, withdraw_base


    def withdrawram(self, authorized_account: str, collection_name: str, recipient: str, bytes: int):
        """
        ## ACTION: atomicdropsx.withdrawram
        - Parametrs:
        methods:
            - authorized_account: name
            - collection_name: name
            - recipient: name
            - bytes: int64
        """

        withdrawram_args = {
            "authorized_account": authorized_account,
            "collection_name": collection_name,
            "recipient": recipient,
            "bytes": bytes
        }
        withdrawram_base = self.generatePayload("atomicdropsx", "withdrawram")
        return withdrawram_args, withdrawram_base

    # ACTIONS END

    def push_actions(self, private_key: str, *actions):
        payloads = []
        for a in actions:
            payloads.append(self.return_payload(a[1], a[0]))

        trx = {
            "actions": payloads
        }
            
        trx['expiration'] = str(
            (dt.datetime.utcnow() + dt.timedelta(seconds=60)).replace(tzinfo=pytz.UTC))

        resp = self.wax.push_transaction(trx, eospy.keys.EOSKey(private_key), broadcast=True)
        return resp, True

    def create_trx(self, private_key: str, **actions):
        ac = []
        for k, v in actions.items():
            ac.append(eval(f'self.{k}({", ".join({v})})'))
        return self.push_actions(private_key, ac)

if __name__ == '__main__':
    contract = atomicdropsx(username="")
    contract.push_actions(
        "",
        contract.transfer(
            _from="",
            to="",
            memo="",
            symbol=""
        )
    )

